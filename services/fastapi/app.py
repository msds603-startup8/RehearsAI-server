import os
import base64
from typing import List

from openai import OpenAI

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import ChatPromptTemplate, MessagesPlaceholder

from langchain_openai import ChatOpenAI

from fastapi.responses import FileResponse
from fastapi import FastAPI, Request, Depends

from pydantic import BaseModel


openai_api_key = os.environ["OPENAI_API_KEY"]

app = FastAPI()
openai_client = OpenAI(api_key=openai_api_key)
langchain_client = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.5, openai_api_key=openai_api_key)

answer_prompt = ChatPromptTemplate.from_messages(
    [
        ('system',
        """You are a professional interviewer in tech domain including data scientist, data engineering, machine learning engineer, data analyist, software engineer.
        You are going to start with an opening and ask interviewee to introduce themselves. After that, you are trying to understand the interviewee's answer,
        and give follow-up questions or the next question.
        """
        ),
        ('placeholder', "{chat_history}"),
        ('human', "{input}")
    ]
)

class InterviewContext(BaseModel):
    interviewee_audio_data: str
    chat_history: List[str] = None
    resume: str = None
    job_description: str = None
    questions: List[str] = None

@app.post("/answer")
async def interview(context: InterviewContext):
    # Save audio bytes to audio file
    input_path = os.path.join("/tmp", "interviewee_speech.mp3")
    with open(input_path, "wb") as file:
        audio_bytes = base64.b64decode(context.interviewee_audio_data.encode('utf-8'))
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
    history = [
         ('human', context.chat_history[i]) if i % 2 == 0
         else  ('ai', context.chat_history[i])
         for i in range(len(context.chat_history))
    ]
    interviewer_text = chain.invoke({'input': interviewee_text, 'chat_history': history}).content

    # Dictate Model
    output_path = os.path.join("/tmp", "speech.mp3")
    with openai_client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="onyx",
            input=interviewer_text
        ) as stt_response:
            stt_response.stream_to_file(output_path)

    with open(output_path, "rb") as audio_file:
        base64_audio_bytes = base64.b64encode(audio_file.read()).decode('utf-8')
        return {
            "interviewer_audio_data" : base64_audio_bytes,
            "dialog" : [interviewee_text, interviewer_text]
        }
