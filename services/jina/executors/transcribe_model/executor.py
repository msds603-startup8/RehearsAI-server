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


class WhisperLocal(Executor):
    """
    A Jina executor that uses a locally loaded Whisper model to
    transcribe audio data into text.

    The `WhisperLocal` class loads a Whisper model (specifically the "base"
    model) for transcribing audio files into text. The transcribed text is
    returned as a `Dialog` object, which can be used for further processing in
    a pipeline.

    Attributes:
        model (Whisper): The Whisper transcription model loaded locally.

    Methods:
        task (doc: Dialog, **kwargs) -> Dialog:
            Extracts audio data from the input `Dialog` object, saves it as an
            MP3 file, and then transcribes it using the locally loaded Whisper
            model. Returns a `Dialog` object containing the transcribed text.
    """
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
        result = self.model.transcribe('input.mp3', language="en", fp16=False,
                                       word_timestamps=False)
        response = Dialog(interviewee_text=result['text'])
        return response


class WhisperAPI(Executor):
    """
    A Jina executor that uses OpenAI's Whisper API to transcribe
    audio data into text.

    The `WhisperAPI` class interfaces with the OpenAI Whisper API
    to transcribe audio files to text. The audio data is extracted from
    an input `Dialog` object, converted to an MP3 file, and sent to the API
    for transcription. The resulting text is packaged into a `Dialog` object
    for further processing.

    Attributes:
        client (OpenAI): An instance of the OpenAI client, configured to
            access the Whisper API.

    Methods:
        task (doc: Dialog, **kwargs) -> Dialog:
            Loads audio data from the input `Dialog` object, saves it as an
            MP3 file, and submits it to the Whisper API for transcription.
            Returns a `Dialog` object containing the transcribed text.
    """
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
