import os
import base64
from typing import List, Tuple

from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate

from pydantic import BaseModel

import openai

from fastapi import FastAPI


openai_api_key = os.environ["OPENAI_API_KEY"]

app = FastAPI()

openai_client = openai.OpenAI(api_key=openai_api_key)
langchain_client = ChatOpenAI(model='gpt-3.5-turbo',
                              temperature=0.5,
                              openai_api_key=openai_api_key)

questions_template_zero_shot = """
You are a helpful assistant tasked with creating interview questions for a data
science position. Below is the resume of the candidate:

{resume_text}

and this is the job description:

{job_description}

Please generate 10 interview questions based on the resume provided:
- 5 technical questions focusing on the candidate’s expertise and experience
with specific technologies, methodologies, and projects.
- 5 behavioral questions that explore how the candidate handles professional
situations, including teamwork, leadership, and problem-solving.

Please format your output in JSON as follows:
{{
  "technical_questions": [
    "Technical Question 1",
    "Technical Question 2",
    "Technical Question 3",
    "Technical Question 4",
    "Technical Question 5"
  ],
  "behavioral_questions": [
    "Behavioral Question 1",
    "Behavioral Question 2",
    "Behavioral Question 3",
    "Behavioral Question 4",
    "Behavioral Question 5",
  ]
}}
"""

answer_prompt = ChatPromptTemplate.from_messages(
    [
        ('system',
            """You are a professional interviewer in tech domain including data
        scientist, data engineering,
        machine learning engineer, data analyist, software engineer.
        You are going to start with an opening and ask interviewee to introduce
        themselves.
        After that, you are trying to understand the interviewee's answer,
        and give follow-up questions or the next question.

        You have the interviewee's resume and the job description summary:
        - Job Description: {job_description}
        - Resume Highlights: {resume}

        Also note that after a followup question you may choose to ask a new
        question.

        Use the conversation history of the interview to make a
        followup question:

        {chat_history}

        Start by asking the interviewee to introduce themselves.
        Use the information provided in the Job description and resume
        to ask relevant follow-up questions based on their responses.
        Also, you may decide to ask a new question after a few
        followup questions, but don't ask more than 3 followup question,
        hence please annotate a followup question and new question.
        Stick only to the list of questions when asking a new
        questions as shown below:

        {questions}

        You may ask technical or a behavioral question,
        but it should be akin to natural human conversation.
        """),
        ('human', "{input}")
    ]
)


class InterviewContext(BaseModel):
    interviewee_audio_data: str = None
    chat_history: List[Tuple[str, str]] = None
    resume: str = None
    job_description: str = None
    questions: List[str] = None


@app.post("/answer")
async def interview(context: InterviewContext):
    """Based on the context (chat_history, resume, job description,
    questions, interviewee's audio reponse),
    answer in audio.

    Returns:
        dict: with two keys (interviewer_audio_data, dialog)
    """
    # Save audio bytes to audio file
    input_path = os.path.join("/tmp", "interviewee_speech.mp3")
    with open(input_path, "wb") as file:
        audio_bytes = base64.b64decode(context.interviewee_audio_data
                                       .encode('utf-8'))
        file.write(audio_bytes)

    interviewee_audio_file = open(input_path, "rb")

    # Transcribe Model
    interviewee_text = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=interviewee_audio_file,
            language="en"
    ).text

    # Language Model
    chain = answer_prompt | langchain_client
    interviewer_text = chain.invoke({
        'input': interviewee_text,
        'chat_history': context.chat_history,
        'job_description': context.job_description,
        'resume': context.resume,
        'questions': context.questions
        }).content

    # Dictate Model
    output_path = os.path.join("/tmp", "speech.mp3")
    with openai_client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="onyx",
                input=interviewer_text
            ) as stt_response:
        stt_response.stream_to_file(output_path)

    with open(output_path, "rb") as audio_file:
        base64_audio_bytes = base64.b64encode(audio_file.read()) \
                                   .decode('utf-8')
        return {
            "interviewer_audio_data": base64_audio_bytes,
            "dialog": [('human', interviewee_text), ('ai', interviewer_text)]
        }


class SummarizeRequest(BaseModel):
    text: str


@app.post("/summarize_resume")
def summarize_resume(request: SummarizeRequest):
    prompt_template = """Write a concise summary of following resume.
    Try to mainly focus on work experience (Employment) and projects:
    "{text}"
    CONCISE SUMMARY:"""
    prompt = PromptTemplate(
                        input_variables=['text'],
                        template=prompt_template
                        )
    llm_chain = LLMChain(llm=langchain_client, prompt=prompt)
    summary = llm_chain.run({'text': request.text})
    return {"summary": summary}


@app.post("/summarize_jd")
def summarize_jd(request: SummarizeRequest):
    prompt_template = """Write a concise summary of following job description:
    "{text}"
    CONCISE SUMMARY:"""
    prompt = PromptTemplate(
                        input_variables=['text'],
                        template=prompt_template
                        )
    llm_chain = LLMChain(llm=langchain_client, prompt=prompt)
    summary = llm_chain.run({'text': request.text})
    return {"summary": summary}


class Questions(BaseModel):
    text: str


@app.post("/create_question")
def create_questions(context: InterviewContext):
    """Method to make question using resume and
    job description calling the openai api"""
    prompt = ChatPromptTemplate.from_messages(messages=[
        ('system', questions_template_zero_shot)
    ])

    chain = prompt | langchain_client
    questions = chain.invoke({
        'resume_text': context.resume,
        'job_description': context.job_description
    })
    return questions.content
