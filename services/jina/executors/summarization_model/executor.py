import os
from jina import Executor, requests
from docarray import DocList
from docarray.documents import TextDoc
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain


openai_api_key = os.environ["OPENAI_API_KEY"]


class OpanAISummarization(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106",
                         api_key=openai_api_key)

        prompt_template = """Write a concise summary of the following:
        "{text}"
        CONCISE SUMMARY:"""
        prompt = PromptTemplate.from_template(prompt_template)

        # Define LLM chain
        llm_chain = LLMChain(llm=llm, prompt=prompt)

        # Define StuffDocumentsChain
        self.stuff_chain = StuffDocumentsChain(llm_chain=llm_chain,
                                               document_variable_name="text")

    @requests
    async def generate(self, docs: DocList[TextDoc],
                       **kwargs) -> DocList[TextDoc]:
        doc = [Document(page_content=docs[0].text)]
        summary = self.stuff_chain.invoke(doc)['output_text']
        responses = DocList[TextDoc]()
        response = TextDoc(text=summary)
        responses.append(response)
        return responses
