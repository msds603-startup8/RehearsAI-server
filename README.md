# RehearsAI-server (Sample)

# How to start
- install Python 3.9
- install ffmepg for STT model and local package
```
# on Mac with brew:
brew install ffmpeg

pip install .
```

- run the flow (you need to set `openai_api_key` in the deployment.py)
```
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES; python flow.py
```