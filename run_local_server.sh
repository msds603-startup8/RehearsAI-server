#!/bin/bash
# Please run this script in the same directory

## Set-up docker image for the models
docker build -t transcribe_model ./executors/transcribe_model
docker build -t language_model ./executors/language_model
docker build -t dictate_model ./executors/dictate_model

## Generate docker-compose.yml
python flow.py

## Run the server
docker compose up