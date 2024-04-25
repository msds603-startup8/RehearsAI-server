#!/bin/bash
# Please run this script in the same directory

## Set-up docker image for the models
docker build --no-cache \
    -t transcribe_model \
    -f ./services/jina/executors/transcribe_model/Dockerfile \
    ./services/jina/executors/transcribe_model/

docker build --no-cache \
    -t language_model \
    -f ./services/jina/executors/language_model/Dockerfile \
    ./services/jina/executors/language_model/

docker build --no-cache \
    -t dictate_model \
    -f ./services/jina/executors/dictate_model/Dockerfile \
    ./services/jina/executors/dictate_model

# Set-up docker image for the streamlit
docker build --no-cache \
    -t streamlit \
    -f ./services/streamlit/Dockerfile \
    ./services/streamlit

## Generate docker-compose.yml
python flow.py

## Run the model server
docker compose --project-name model_server up -d

## Run the streamlit server & Delete the docker compose containers
docker run -p 8080:8080 streamlit -- --host host.docker.internal ; docker compose down

