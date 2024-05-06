import os
from jina import Executor, requests
from docarray import DocList
from docarray.documents import TextDoc, AudioDoc
from openai import OpenAI
from typing import List, Dict
from docarray import BaseDoc
from docarray.typing import AudioBytes, AudioUrl


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


class DictateModel(Executor):
    """
    A Jina executor that transforms text input into an audio output
    using OpenAI's Text-to-Speech (TTS) API.

    The `DictateModel` class integrates with OpenAI's TTS services to generate
    speech from provided text. When the `task` method is called, it sends the
    input text to the TTS model specified (default: `tts-1`), retrieves the
    streaming audio response, and writes it to a file. It then packages the
    audio data as bytes in a `Dialog` object for further processing.

    Attributes:
        model (OpenAI): An instance of the OpenAI API client configured
        with an API key.

    Methods:
        task (doc: Dialog, **kwargs) -> Dialog:
            Converts the given text input into a streaming audio file using
            OpenAI's TTS model, saves it to a file, and returns an audio
            document containing the byte data of the file.
    """
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
