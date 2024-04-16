import os

from jina import Executor, requests

from docarray import DocList
from docarray.documents import TextDoc, AudioDoc

import whisper

from openai import OpenAI


openai_api_key = os.environ["OPENAI_API_KEY"]

class WhisperLocal(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = whisper.load_model("base")

    @requests
    async def generate(self, docs: DocList[AudioDoc], **kwargs) -> DocList[TextDoc]:
        print("TranscribeModel called")

        docs[0].tensor.save(
            file_path='input.mp3',
            format='mp3',
            frame_rate=docs[0].frame_rate
        )

        result = self.model.transcribe("input.mp3", language="en", fp16=False, word_timestamps=False)
        responses = DocList[TextDoc]()
        response = TextDoc(text=result['text'])
        responses.append(response)
        return responses
    
class WhisperAPI(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = OpenAI(api_key=openai_api_key)

    @requests
    async def generate(self, docs: DocList[AudioDoc], **kwargs) -> DocList[TextDoc]:
        docs[0].tensor.save(
            file_path='input.mp3',
            format='mp3',
            frame_rate=docs[0].frame_rate
        )

        audio_file= open("input.mp3", "rb")
        result = self.client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            language="en"
        )

        responses = DocList[TextDoc]()
        response = TextDoc(text=result.text)
        responses.append(response)
        return responses