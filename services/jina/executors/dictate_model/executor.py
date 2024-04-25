import os 

from jina import Executor, requests

from docarray import DocList
from docarray.documents import TextDoc, AudioDoc

from openai import OpenAI

from typing import List, Dict
from docarray import BaseDoc
from docarray.typing import AudioBytes, AudioUrl


class Dialog(BaseDoc):
    interviewee_speech_bytes: AudioBytes = None
    chat_history: List[str] = None
    interviewee_text: str = None
    interviewer_text: str = None
    interviewer_speech_bytes: AudioBytes = None
    metadata: Dict = None

openai_api_key = os.environ["OPENAI_API_KEY"]

class DictateModel(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = OpenAI(api_key=openai_api_key)
        
    @requests
    async def task(self, doc: Dialog, **kwargs) -> Dialog:
        print("DictateModel called")
        with self.model.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="onyx",
            input=doc.interviewer_text
        ) as stt_response:
            stt_response.stream_to_file("speech.mp3")
        doc = AudioDoc(url="speech.mp3")
        response = Dialog(interviewer_speech_bytes=doc.url.load_bytes())
        return response