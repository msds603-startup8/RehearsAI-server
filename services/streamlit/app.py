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

def send_for_summarization_jd(text):
    # Assuming FastAPI is running on localhost and port 8000
    url = "http://localhost:8000/summarize_jd"
    try:
        response = requests.post(url, json={"text": text})
        if response.status_code == 200:
            return response.json()['summary']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Network error: {str(e)}"

def send_for_summarization_resume(text):
    # Assuming FastAPI is running on localhost and port 8000
    url = "http://localhost:8000/summarize_resume"
    try:
        response = requests.post(url, json={"text": text})
        if response.status_code == 200:
            return response.json()['summary']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Network error: {str(e)}"



# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'input'

# Page to collect PDF and text input
if st.session_state.page == 'input':
    st.header("Upload PDF and Enter Job Description")
    resume = st.file_uploader("Upload your PDF", type='pdf')
    jd = st.text_area('Copy and paste job description.')
    
    if st.button('Start Session'):
        resume_text = ""
        if resume is not None:
            pdf_reader = PdfReader(resume)
            for page in pdf_reader.pages:
                resume_text += page.extract_text() or " "  # Handle pages with no text
        st.session_state.resume_summary = send_for_summarization_resume(resume_text)
        st.session_state.jd_summary = send_for_summarization_jd(jd)
        st.session_state.page = 'conversation'


# Page for conversation with virtual assistant
if st.session_state.page == 'conversation':
    st.title("RehearsAI Testing: Talking Voice Assistant")
    st.subheader("Summarized Job Description:")
    st.write(st.session_state.jd_summary)
    st.subheader("Summarized PDF Text:")
    st.write(st.session_state.resume_summary)

    audio_bytes = audio_recorder()
    if audio_bytes:
        response = requests.post(
            f"http://{args.host}:8000/answer",
            data=audio_bytes,
            headers={'Content-Type': 'application/octet-stream'}
        )
        autoplay_audio(response.content)