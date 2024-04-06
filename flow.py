import os 
from jina import Flow
from deployment import TranscribeModel, LanguageModel, DictateModel

# https://github.com/jina-ai/jina/issues/3025
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

flow = (
    Flow(port=12345)
    .add(uses=TranscribeModel, timeout_ready=-1)
    .add(uses=LanguageModel, timeout_ready=-1)
    .add(uses=DictateModel, timeout_ready=-1)
)

with flow:
    flow.block()