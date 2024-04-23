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

def main():
    st.header("Upload PDF")
    pdf = st.file_uploader("Upload your PDF", type = 'pdf')
    if pdf is not None: # Added missing if statement
        pdf_reader = PdfReader(pdf)

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        #st.write(text)

if __name__ == '__main__':
    main()


st.title("RehearsAI Testing: Talking Voice Assistant")

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

