from typing import List, Dict
import base64
import argparse

import requests
import json

from PyPDF2 import PdfReader

import streamlit as st
from audio_recorder_streamlit import audio_recorder


parser = argparse.ArgumentParser(description='Example script with a host argument')
parser.add_argument('--host', default='0.0.0.0', required=False, help='The host address to connect to')
args = parser.parse_args()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

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
        st.session_state.resume = resume_text
        st.session_state.job_description = jd
        st.session_state.resume_summary = send_for_summarization_resume(resume_text)
        st.session_state.job_desc_summary = send_for_summarization_jd(jd)

        interview_context_data = {
            "resume": st.session_state.resume,
            "job_description": st.session_state.job_description
        }

        # Send InterviewContext to the server
        response = requests.post(
            f"http://{args.host}:8000/create_question",
            json={
                "resume": st.session_state.resume,
                "job_description": st.session_state.job_description
            },
            headers={'Content-Type': 'application/json'}
        )

        
        if response.ok:
            response_data = json.loads(response.content.decode('utf-8'))
            questions_list = response_data.split('\n\n')
            st.session_state.page = 'conversation'
            st.success("Session started successfully!")
            st.session_state.questions = questions_list
        else:
            st.error("Failed to start session.")


# Page for conversation with virtual assistant
if st.session_state.page == 'conversation':
    st.title("RehearsAI Testing: Talking Voice Assistant")

    audio_bytes = audio_recorder()
    if audio_bytes:
        response = requests.post(
            f"http://{args.host}:8000/answer",
            json={
                "interviewee_audio_data": base64.b64encode(audio_bytes).decode('utf-8'),
                "chat_history": st.session_state.chat_history,
                "job_description": st.session_state.job_description,
                "resume": st.session_state.resume,
                "questions": st.session_state.questions
            },
            headers={'Content-Type': 'application/json'}
        )

        response_data = response.json()
        interviewer_audio_data = response_data['interviewer_audio_data']
        dialog = response_data['dialog']
        st.session_state.chat_history.extend(dialog)
        audio_bytes = base64.b64decode(interviewer_audio_data.encode('utf-8'))
        st.audio(audio_bytes)