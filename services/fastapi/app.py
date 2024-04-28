import os
import io
import base64

import numpy as np

from typing import Annotated

from openai import OpenAI

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from fastapi.responses import FileResponse
from fastapi import FastAPI

from langchain.chains import LLMChain
from langchain import PromptTemplate

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel

openai_api_key = os.environ["OPENAI_API_KEY"]

app = FastAPI()
openai_client = OpenAI(api_key=openai_api_key)
langchain_client = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.5, openai_api_key=openai_api_key)

answer_prompt = ChatPromptTemplate(messages=
    [
        SystemMessage(
            content="""You are a professional interviewer in tech domain including data scientist, data engineering, machine learning engineer, data analyist, software engineer.
            You are going to start with an opening and ask interviewee to introduce themselves. After that, you are trying to understand the interviewee's answer,
            and give follow-up questions or the next question."""
        ),
        HumanMessage(
            content="{input}"
        ),
    ]
)


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

    # Transcribe Model
    interviewee_text = openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=interviewee_audio_file,
            language="en"
    ).text
    
    # Language Model
    chain = answer_prompt | langchain_client
    interviewer_text = chain.invoke({'input': interviewee_text}).content

    # Dictate Model
    output_path = os.path.join("/tmp", "speech.mp3")
    with openai_client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="onyx",
            input=interviewer_text
        ) as stt_response:
            stt_response.stream_to_file(output_path)

    return FileResponse(output_path)


class SummarizeRequest(BaseModel):
    text: str


@app.post("/summarize_resume")
def summarize_resume(request: SummarizeRequest):
    prompt_template = """Write a concise summary of following resume. Try to mainly focus on work experience (Employment) and projects:
    "{text}"
    CONCISE SUMMARY:"""
    prompt=PromptTemplate(
    input_variables=['text'],
    template=prompt_template
)
    llm_chain=LLMChain(llm=langchain_client, prompt=prompt)
    summary=llm_chain.run({'text':request.text})
    return {"summary": summary}


@app.post("/summarize_jd")
def summarize_jd(request: SummarizeRequest):
    prompt_template = """Write a concise summary of following job description:
    "{text}"
    CONCISE SUMMARY:"""
    prompt=PromptTemplate(
    input_variables=['text'],
    template=prompt_template
)
    llm_chain=LLMChain(llm=langchain_client, prompt=prompt)
    summary=llm_chain.run({'text':request.text})
    return {"summary": summary}