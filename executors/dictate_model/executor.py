import os 

from jina import Executor, requests

from docarray import DocList
from docarray.documents import TextDoc, AudioDoc

from openai import OpenAI

openai_api_key = os.environ["OPENAI_API_KEY"]

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