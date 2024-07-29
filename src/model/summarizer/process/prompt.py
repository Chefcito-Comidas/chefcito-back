from typing import List

from pydantic import SecretStr
from src.model.opinions.opinion import Opinion
from src.model.summarizer.summary import Summary
from langchain_core.prompts import PromptTemplate 
from langchain.chains.llm import LLMChain
from langchain_google_vertexai import VertexAIModelGarden

def get_template() -> PromptTemplate:
    map_template = """The following is a set of opinions
    {opinions}
    Based on this list of opinions, please generate a summarized
    opinion:
    """
    return PromptTemplate.from_template(map_template)


def get_llm(project: str, endpoint: str) -> VertexAIModelGarden:
    return VertexAIModelGarden(
            project=project,
            endpoint_id=endpoint
            )

def create_prompt(llm: VertexAIModelGarden, opinions: List[Opinion], summaries: List[Summary]):
     chain = LLMChain(llm=llm, prompt=get_template()) 
