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

## How to run Model Server?
Currently, you can run the model server locally only in docker containers.
Entry point for the server is `0.0.0.0:12345`.

### Run the model server in docker containers

- Install docker
https://docs.docker.com/engine/install/

- Set-up openai-api-key
```bash
export OPENAI_API_KEY=...
```

- Set-up docker images for the models and run the server
```bash
./run_local_server.sh
```

## How to run Web Server?
On the top of running the model server, you can also run the web server and let it interact with the model server through web browser. There are two ways to run the web server locally.

### Run the streamlit web server in docker container
```bash
docker build -t web_server web
docker run -p 8080:8080 web_server -- --host host.docker.internal
```

### Run the streamlit web server in localhost
```bash
pip install -r web/requirements.txt
streamlit run web/app.py
```
