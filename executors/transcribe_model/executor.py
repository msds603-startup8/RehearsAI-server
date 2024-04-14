from jina import Executor, requests

from docarray import DocList
from docarray.documents import TextDoc, AudioDoc

import whisper


class TranscribeModel(Executor):
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