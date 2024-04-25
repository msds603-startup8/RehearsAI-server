import os

from jina import Executor, requests

from docarray import DocList
from docarray.documents import TextDoc, AudioDoc

import whisper

from openai import OpenAI

from typing import List, Dict
from docarray import BaseDoc
from docarray.typing import AudioBytes


class Dialog(BaseDoc):
    interviewee_speech_bytes: AudioBytes = None
    chat_history: List[str] = None
    interviewee_text: str = None
    interviewer_text: str = None
    interviewer_speech_bytes: AudioBytes = None
    metadata: Dict = None

openai_api_key = os.environ["OPENAI_API_KEY"]

class WhisperLocal(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = whisper.load_model("base")

    @requests
    async def task(self, doc: Dialog, **kwargs) -> Dialog:
        tensor, frame_rate = doc.interviewee_speech_bytes.load()
        tensor.save(
            file_path='input.mp3',
            format='mp3',
            frame_rate=frame_rate
        )
        result = self.model.transcribe('input.mp3', language="en", fp16=False, word_timestamps=False)
        response = Dialog(interviewee_text=result['text'])
        return response
    
class WhisperAPI(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = OpenAI(api_key=openai_api_key)

    @requests
    async def task(self, doc: Dialog, **kwargs) -> Dialog:
        tensor, frame_rate = doc.interviewee_speech_bytes.load()
        tensor.save(
            file_path='input.mp3',
            format='mp3',
            frame_rate=frame_rate
        )

        audio_file = open('input.mp3', "rb")
        result = self.client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            language="en"
        )

        response = Dialog(interviewee_text=result.text)
        return response