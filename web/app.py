import sys
import os
import argparse

from jina import Client
from docarray import DocList
from docarray.documents import AudioDoc
from PyPDF2 import PdfReader


import streamlit as st
from audio_recorder_streamlit import audio_recorder

parser = argparse.ArgumentParser(description='Example script with a host argument')
parser.add_argument('--host', default='0.0.0.0', required=False, help='The host address to connect to')
args = parser.parse_args()

client = Client(host=args.host, port=12345)

# st.header("Upload PDF")
# pdf = st.file_uploader("Upload your resume", type = 'pdf')
# if pdf is not None:
#     pdf_reader = PdfReader(pdf)

#     text = ""
#     for page in pdf_reader.pages:
#         text += page.extract_text()

# jd = st.text_input('Copy and paste job description.')
# st.write(jd)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'input'

# Page to collect PDF and text input
if st.session_state.page == 'input':
    st.header("Upload PDF and Enter Job Description")
    pdf = st.file_uploader("Upload your PDF", type='pdf')
    jd = st.text_area('Copy and paste job description.')
    
    if st.button('Submit'):
        st.session_state.pdf_text = ""
        if pdf is not None:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                st.session_state.pdf_text += page.extract_text()
        st.session_state.jd = jd
        st.session_state.page = 'conversation'

# Page for conversation with virtual assistant
if st.session_state.page == 'conversation':
    st.title("RehearsAI Testing: Talking Voice Assistant")
    # st.write("PDF Text Extracted: ", st.session_state.pdf_text)
    # st.write("Job Description: ", st.session_state.jd)

    audio_bytes = audio_recorder()
    if audio_bytes:
        ## Save the recorded file
        input_file_path = "audio_file.mp3"
        with open(input_file_path, "wb") as f:
            f.write(audio_bytes)
        
        input_audio = AudioDoc(url=input_file_path)
        input_audio.tensor, input_audio.frame_rate = input_audio.url.load()
        input_audio.bytes_ = input_audio.tensor.to_bytes()

        print("requested..")
        r = client.post(on='/', inputs=DocList[AudioDoc]([input_audio]), return_type=DocList[AudioDoc])
        print("done..")

        # ## Read out the text response using tts
        speech_file_path = 'audio_response.mp3'
        tensor_reversed = r[0].tensor
        tensor_reversed.save(
            file_path=speech_file_path,
            format='mp3',
            frame_rate=r[0].frame_rate,
        )
        st.audio(speech_file_path)

