import sys
import os
import base64
import argparse

import requests
import json

from typing import List, Dict
from docarray import BaseDoc
from PyPDF2 import PdfReader

import streamlit as st
from audio_recorder_streamlit import audio_recorder


parser = argparse.ArgumentParser(description='Example script with a host argument')
parser.add_argument('--host', default='0.0.0.0', required=False, help='The host address to connect to')
args = parser.parse_args()

class InterviewContext(BaseDoc):
    resume_text: str = None
    job_description: str = None

def autoplay_audio(data):
    # https://discuss.streamlit.io/t/how-to-play-an-audio-file-automatically-generated-using-text-to-speech-in-streamlit/33201/2
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

        interview_context_data = {
            "resume_text": st.session_state.resume,
            "job_description": st.session_state.jd
        }

        # Send InterviewContext to the server
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            f"http://{args.host}:8000/init_session",
            data=json.dumps(interview_context_data),
            headers=headers
        )

        if response.ok:
            st.session_state.page = 'conversation'
            st.success("Session started successfully!")
        else:
            st.error("Failed to start session.")

# Page for conversation with virtual assistant
if st.session_state.page == 'conversation':
    st.title("RehearsAI Testing: Talking Voice Assistant")
    # st.write("PDF Text Extracted: ", st.session_state.pdf_text)
    # st.write("Job Description: ", st.session_state.jd)

    audio_bytes = audio_recorder()
    if audio_bytes:
        response = requests.post(
            f"http://{args.host}:8000/answer",
            data=audio_bytes,
            headers={'Content-Type': 'application/octet-stream'}
        )
        autoplay_audio(response.content)