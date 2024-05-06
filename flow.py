import os
from jina import Flow

# https://github.com/jina-ai/jina/issues/3025
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

flow = (
    Flow(port=12345)
    .add(
        uses="docker://transcribe_model",
        timeout_ready=-1,
        name='transcribe_model',
        env={'OPENAI_API_KEY': os.environ["OPENAI_API_KEY"]}
    )
    .add(
        uses="docker://language_model",
        timeout_ready=-1,
        name='language_model',
        env={'OPENAI_API_KEY': os.environ["OPENAI_API_KEY"]}
    )
    .add(
        uses="docker://dictate_model",
        timeout_ready=-1,
        name='dictate_model',
        env={'OPENAI_API_KEY': os.environ["OPENAI_API_KEY"]}
    )
)

flow.to_docker_compose_yaml('docker-compose.yml')
