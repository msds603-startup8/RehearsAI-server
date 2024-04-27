import sys
import os
import base64
import argparse

import requests

from typing import List, Dict
from PyPDF2 import PdfReader

import streamlit as st
from audio_recorder_streamlit import audio_recorder


parser = argparse.ArgumentParser(description='Example script with a host argument')
parser.add_argument('--host', default='0.0.0.0', required=False, help='The host address to connect to')
args = parser.parse_args()

def autoplay_audio(data):
    # https://discuss.streamlit.io/t/how-to-play-an-audio-file-automatically-generated-using-text-to-speech-in-streamlit/33201/2
    md = f"""
        <div style="display: none;">
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{data}" type="audio/mp3">
            </audio>
        </div>
        """
    st.markdown(
        md,
        unsafe_allow_html=True,
    )

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

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
        response = requests.post(
            f"http://{args.host}:8000/answer",
            json={
                "interviewee_audio_data": base64.b64encode(audio_bytes).decode('utf-8'),
                "chat_history": st.session_state.chat_history 
            },
            headers={'Content-Type': 'application/json'}
        )

        response_data = response.json()
        interviewer_audio_data = response_data['interviewer_audio_data']
        dialog = response_data['dialog']
        st.session_state.chat_history.extend(dialog)
        audio_bytes = base64.b64decode(interviewer_audio_data.encode('utf-8'))
        st.audio(audio_bytes)