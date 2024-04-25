import sys
import os
import base64
import argparse
from typing import List, Dict

from jina import Client
from docarray.documents import TextDoc
from docarray import BaseDoc
from docarray.typing import AudioBytes

from PyPDF2 import PdfReader

import streamlit as st
from audio_recorder_streamlit import audio_recorder


class Dialog(BaseDoc):
    interviewee_speech_bytes: AudioBytes = None
    chat_history: List[str] = None
    interviewee_text: str = None
    interviewer_text: str = None
    interviewer_speech_bytes: AudioBytes = None
    metadata: Dict = None

parser = argparse.ArgumentParser(description='Example script with a host argument')
parser.add_argument('--host', default='0.0.0.0', required=False, help='The host address to connect to')
args = parser.parse_args()

client = Client(host=args.host, port=12345)

def autoplay_audio(data):
    b64 = base64.b64encode(data).decode()
    md = f"""
        <div style="display: none;">
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        </div>
        """
    st.markdown(
        md,
        unsafe_allow_html=True,
    )

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'input'

# Page to collect PDF and text input
if st.session_state.page == 'input':
    st.header("Upload PDF and Enter Job Description")
    resume = st.file_uploader("Upload your PDF", type='pdf')
    jd = st.text_area('Copy and paste job description.')
    
    if st.button('Start Session'):
        st.session_state.resume = ""
        if resume is not None:
            pdf_reader = PdfReader(resume)
            for page in pdf_reader.pages:
                st.session_state.resume += page.extract_text()
        st.session_state.jd = jd
        st.session_state.page = 'conversation'

# Page for conversation with virtual assistant
if st.session_state.page == 'conversation':
    st.title("RehearsAI Testing: Talking Voice Assistant")
    # st.write("PDF Text Extracted: ", st.session_state.pdf_text)
    # st.write("Job Description: ", st.session_state.jd)

    audio_bytes = audio_recorder()
    if audio_bytes:
        response = client.post(on='/',
            inputs=Dialog(
                interviewee_speech_bytes=AudioBytes(audio_bytes)
            ),
            return_type=Dialog
        )
        autoplay_audio(response.interviewer_speech_bytes)