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

## Quick Start
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
./run_demo.sh
# Now you can see the demo at http://0.0.0.0:8080
```
