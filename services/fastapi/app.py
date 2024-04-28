import os
import io
import base64

import numpy as np
import json

from typing import Annotated

from openai import OpenAI

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from fastapi.responses import FileResponse
from fastapi import FastAPI

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import openai
from langchain.prompts import PromptTemplate



openai_api_key = os.environ["OPENAI_API_KEY"]

app = FastAPI()
openai_client = OpenAI(api_key=openai_api_key)
langchain_model = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.5, openai_api_key=openai_api_key)

class InterviewContext(BaseModel):
    resume_text: str
    job_description: str

questions_template_zero_shot="""
You are a helpful assistant tasked with creating interview questions for a data science position. Below is the resume of the candidate:

{resume_text}

and this is the job description:

{job_description}

Please generate 10 interview questions based on the resume provided:
- 5 technical questions focusing on the candidate’s expertise and experience with specific technologies, methodologies, and projects.
- 5 behavioral questions that explore how the candidate handles professional situations, including teamwork, leadership, and problem-solving.
"""

system_message_content = """
You are a professional interviewer in tech domain including data scientist, data engineering, 
machine learning engineer, data analyist, software engineer.
You are going to start with an opening and ask interviewee to introduce themselves. 
After that, you are trying to understand the interviewee's answer,
and give follow-up questions or the next question. 

You have the interviewee's resume and the job description:
- Job Description: {job_description}
- Resume Highlights: {resume_highlights}

Also note that after a followup question you may choose to ask a new question.

Use the conversation history of the interview to make a followup question:

{conversation_history}

Start by asking the interviewee to introduce themselves. Use the information provided in the Job description and resume
to ask relevant follow-up questions based on their responses. Also, you may decide to ask a new question after a few 
followup questions, but don't ask more than 3 followup question, hence please annotate a followup question and new question.
Stick only to the list of questions when asking a new questions as shown below:

{questions}

You may ask technical or a behavioral question, but it should be akin to natural human conversation.
"""

conversation_history = ""

user_data = {}

summarised_user_data = {}

questions = {}

# answer_prompt = ChatPromptTemplate(messages=
#     [
#         SystemMessage(
#             content="""You are a professional interviewer in tech domain including data scientist, data engineering, machine learning engineer, data analyist, software engineer.
#             You are going to start with an opening and ask interviewee to introduce themselves. After that, you are trying to understand the interviewee's answer,
#             and give follow-up questions or the next question."""
#         ),
#         HumanMessage(
#             content="{input}"
#         ),
#     ]
# )

def summarize_text_job_desc(text, model="gpt-3.5-turbo"):
    prompt = "Summarize the following text but do not change any requirements listed in the job description:\n\n{text}"
    prompt = prompt.format(text=text)
    messages = [{"role": "user", "content": prompt}]
    response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=300,
        )
    return response

def summarize_text_resume(text, model="gpt-3.5-turbo"):
    prompt = "Summarize the following text but do not change any skills, experience, education or projects in the resume:\n\n{text}"
    prompt = prompt.format(text=text)
    messages = [{"role": "user", "content": prompt}]
    response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=300,
        )
    return response

def update_conversation_history(conversation_history, new_message, speaker):
    """
    Update the conversation history string with the new message.
    """
    return f"{conversation_history}\n{speaker}: {new_message}"

def answer_prompt(job_description, resume):
    """
    Function to create an answer prompt
    """
    job_summary = summarize_text_job_desc(job_description, langchain_model, openai_api_key)
    resume_summary = summarize_text_resume(resume, langchain_model, openai_api_key)

    return ChatPromptTemplate(
        input_variables=['job_description', 'resume_highlights'],
        messages=[
            SystemMessage(content=system_message_content.format(
                job_description=job_summary,
                resume_highlights=resume_summary
            ))
        ]
    )

def create_questions(resume:str, job_description:str):
     """Method to make question using resume and job description calling the openai api"""
     prompt_zero_shot = PromptTemplate(
        template=questions_template_zero_shot,
        input_variables=["resume_text","job_description"],
        )
     formatted_prompt_zero_shot = prompt_zero_shot.format(resume_text=resume, job_description=job_description)

     messages = [{
    "role": "system",
    "content": formatted_prompt_zero_shot
    }]  

     response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
            temperature=0,
    )
     questions = json.loads(response.choices[0].message.content)
     return questions

@app.post("/init_session")
def init_session(context: InterviewContext):
    if not context.resume_text or not context.job_description:
        raise HTTPException(status_code=400, detail="Empty resume or job description provided.")

    user_data['resume'] = context.resume_text
    user_data['job_desc'] = context.job_description

    summarised_user_data['resume'] = summarize_text_resume(context.resume_text)
    summarised_user_data['job_desc'] = summarize_text_job_desc(context.job_description)

    questions['questions'] = create_questions(resume=context.resume_text, job_description=context.job_description)
    
    return JSONResponse(status_code=200, content={"status": "success", "message": "Session initialized with provided data."})

async def parse_body(request: Request):
    data: bytes = await request.body()
    return data

@app.post("/answer")
async def interview(data: bytes = Depends(parse_body)):
    # Save audio bytes to audio file
    input_path = os.path.join("/tmp", "interviewee_speech.mp3")
    with open(input_path, "wb") as file:
        file.write(data)

    interviewee_audio_file = open(input_path, "rb")

    global conversation_history
    
    conversation_history = update_conversation_history(conversation_history=conversation_history, \
                                                       new_message=interviewee_text, speaker="Interviwee")

    # Transcribe Model
    interviewee_text = openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=interviewee_audio_file,
            language="en"
    ).text
    
    answer_prompt = answer_prompt(questions=questions["questions"],
                                  conversation_history=conversation_history)
    
    # Language Model
    chain = answer_prompt | langchain_model
    interviewer_text = chain.invoke({'input': conversation_history}).content

    conversation_history = update_conversation_history(conversation_history=conversation_history, \
                                                       new_message=interviewer_text, speaker="Interviewer")

    # Dictate Model
    output_path = os.path.join("/tmp", "speech.mp3")
    with openai_client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="onyx",
            input=interviewer_text
        ) as stt_response:
            stt_response.stream_to_file(output_path)

    return FileResponse(output_path)
