import os

from jina import Executor, requests

from docarray import DocList
from docarray.documents import TextDoc

from typing import List, Dict
from docarray import BaseDoc
from docarray.typing import AudioBytes

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class Dialog(BaseDoc):
    interviewee_speech_bytes: AudioBytes = None
    chat_history: List[str] = None
    interviewee_text: str = None
    interviewer_text: str = None
    interviewer_speech_bytes: AudioBytes = None
    metadata: Dict = None

openai_api_key = os.environ["OPENAI_API_KEY"]

class OpenAISingleTurnLanguageModel(Executor):
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
    async def task(self, doc: Dialog, **kwargs) -> Dialog:
        chain = self.prompt | self.model
        result = chain.invoke({'input': doc.interviewee_text})
        response = Dialog(interviewer_text=result.content)
        return response