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
    """
    A data structure representing the context and audio data for
    an interview session.

    The `Dialog` class serves as a container for both the textual
    and audio data involved in an interview  session. It contains
    attributes for storing audio data in byte format, as well as the
    text inputs for both the interviewer and the interviewee. This data
    structure can be processed further by other executors or pipelines to
    perform additional tasks like generating speech or conducting analysis.

    Attributes:
        interviewee_speech_bytes (AudioBytes): The raw audio data of the
            interviewee's speech.
        chat_history (List[str]): A list of conversation exchanges between
            the interviewer and interviewee.
        interviewee_text (str): The textual transcript of the
            interviewee's speech.
        interviewer_text (str): The textual input of the interviewer's
            questions or prompts.
        interviewer_speech_bytes (AudioBytes): The raw audio data of the
            interviewer's generated speech.
        metadata (Dict): Additional metadata related to the interview session,
            such as timestamps or speaker IDs.
    """
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
        self.model = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.5,
                                openai_api_key=openai_api_key)
        self.prompt = ChatPromptTemplate(messages=[
                SystemMessage(
                    content="""You are a professional interviewer in tech
                    domain including data scientist, data engineering, machine
                    learning engineer, data analyist, software engineer.
                    You are going to start with an opening and ask interviewee
                    to introduce themselves. After that, you are trying to
                    understand the interviewee's answer, and give follow-up
                    questions or the next question."""
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
