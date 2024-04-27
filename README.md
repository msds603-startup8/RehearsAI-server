# RehearsAI

## Structure
```
# web: streamlit web server
# executors: components in model server

🌳 project
├── 📄 README.md
├── 📁 executors
│   ├── 📁 dictate_model
│   │   ├── 📄 Dockerfile
│   │   ├── 📄 README.md
│   │   ├── 📄 config.yml
│   │   ├── 📄 executor.py
│   │   └── 📄 requirements.txt
│   ├── 📁 language_model
│   │   ├── 📄 Dockerfile
│   │   ├── 📄 README.md
│   │   ├── 📄 config.yml
│   │   ├── 📄 executor.py
│   │   └── 📄 requirements.txt
│   └── 📁 transcribe_model
│       ├── 📄 Dockerfile
│       ├── 📄 README.md
│       ├── 📄 config.yml
│       ├── 📄 executor.py
│       └── 📄 requirements.txt
├── 📄 flow.py
├── 📄 run_local_server.sh
├── 📁 test
│   └── 📄 test_example.py
└── 📁 web
    ├── 📄 Dockerfile
    ├── 📄 app.py
    └── 📄 requirements.txt
```
## Quick Start (In Local Environment)
- Set-up openai-api-key
```bash
export OPENAI_API_KEY=...
```

- Install required package and library
```bash
(streamlit - web) pip install -r ./services/streamlit/requirements.txt
(fastapi - model) pip install -r ./services/fastapi/requirements.txt
```

- Run the streamlit server & fastapi server
```bash
(streamlit - web) streamlit run ./services/streamlit/app.py
(fastapi - model) uvicorn services.fastapi.app:app --port 8000
```

## Quick Start (In Docker Container)

- Install docker
https://docs.docker.com/engine/install/

- Set-up docker images
```bash
docker build --no-cache \
    -t streamlit \
    -f ./services/streamlit/Dockerfile \
    ./services/streamlit

docker build --no-cache \
    -t fastapi \
    -f ./services/fastapi/Dockerfile \
    ./services/fastapi
```

- Run the web & model server
```bash
# Run fastapi server
docker run -e "OPENAI_API_KEY={your_openai_api_key}" -p 8000:8000 fastapi

# Run streamlit server
docker run -e "OPENAI_API_KEY={your_openai_api_key}" -p 8080:8080 streamlit -- --host host.docker.internal
# Now you can see the demo at http://0.0.0.0:8080
```
