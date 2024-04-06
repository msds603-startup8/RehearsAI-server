from time import time

import torch

import whisper

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts.chat import ChatPromptTemplate

from langchain_openai import ChatOpenAI
from openai import OpenAI

from jina import Executor, requests
from docarray import DocList
from docarray.documents import TextDoc, AudioDoc
from docarray.typing import AudioNdArray

import numpy as np

openai_api_key = "..."

class TranscribeModel(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = whisper.load_model("base")

    @requests
    async def generate(self, docs: DocList[AudioDoc], **kwargs) -> DocList[TextDoc]:
        print("TranscribeModel called")
        np_array = docs[0].tensor.unwrap().astype(np.float32)
        result = self.model.transcribe(np_array, language="en", fp16=False, word_timestamps=False)
        responses = DocList[TextDoc]()
        response = TextDoc(text=result['text'])
        responses.append(response)
        return responses

class LanguageModel(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.5, openai_api_key=openai_api_key)
        self.prompt = ChatPromptTemplate(messages=
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

    @requests
    async def generate(self, docs: DocList[TextDoc], **kwargs) -> DocList[TextDoc]:
        print("LanguageModel called")
        chain = self.prompt | self.model
        result = chain.invoke({'input': docs[0].text})
        responses = DocList[TextDoc]()
        response = TextDoc(text=result.content)
        responses.append(response)
        return responses

class DictateModel(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = OpenAI(api_key=openai_api_key)
        

    @requests
    async def generate(self, docs: DocList[TextDoc], **kwargs) -> DocList[AudioDoc]:
        print("DictateModel called")
        with self.model.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="onyx",
            input=docs[0].text
        ) as stt_response:
            stt_response.stream_to_file("speech.mp3")
        responses = DocList[AudioDoc]()
        response = AudioDoc(url="speech.mp3")
        response.tensor, response.frame_rate = response.url.load()
        responses.append(response)
        return responses
