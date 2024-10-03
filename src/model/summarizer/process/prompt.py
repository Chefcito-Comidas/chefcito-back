import json
from logging import log
import logging
from typing import Any, Dict, List, Tuple

from langchain_core.documents import Document

from src.model.commons.logger import Logger
from src.model.opinions.opinion import Opinion
from src.model.summarizer.summary import Summary
from langchain_core.prompts import PromptTemplate 
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain, ReduceDocumentsChain 
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_vertexai.llms import VertexAI
import google.auth as auth

llm: VertexAI | None = None

def get_cred(private_key: str, private_key_id: str) -> Dict:
    cred = {
            "type": "service_account",
            "project_id": "chefcito-comidas",
            "private_key_id": private_key_id,
            "private_key": bytes.fromhex(private_key).decode(),
            "client_email": "summarizer-service@chefcito-comidas.iam.gserviceaccount.com",
            "client_id": "100286983511312951818",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/summarizer-service%40chefcito-comidas.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
            }
    return cred

def init_google(private_key: str, private_key_id: str) -> Tuple[Any, str | None]:
    cred = get_cred(private_key, private_key_id) 
    return auth.load_credentials_from_dict(cred)

def init(private_key: str, private_key_id: str, model: str = 'gemini-1.0-pro'):
    global llm
    creds, project = init_google(private_key, private_key_id)
    llm = VertexAI(
            project=project,
            model_name=model,
            credentials=creds
            )

def get_template() -> PromptTemplate:
    map_template = """The following is a set of opinions about a single restaurant
    {opinions}
    Based on this list of opinions, please generate a summarized
    opinion. The summary should take into account the date of the opinions and
    show how to they changed over time without being explicit the time at which each
    opinion was given. If the opinions contain no relevant information for a restaurant, don't use them to create a summary.
    the output should be in spanish and it shouldn't be a longer than a paragraph.
    The output must not contain the name of the restaurant and it should be written in plain spanish and only using letters and punctiation marks.
    """
    return PromptTemplate.from_template(map_template)


def get_llm() -> VertexAI:
    global llm
    if llm == None:
        raise Exception("Prompt model not yet initialized")
    return llm

def turn_opinions_to_text(opinions: List[Opinion]) -> List[str]:
    return list(
            map(lambda opinion: f"opinion from {opinion.date}: {opinion.opinion}",
               opinions)
            )

def turn_summaries_to_text(summaries: List[Summary]) -> List[str]:
    return list(
            map(lambda summ: f"Summary of opinions up to {summ.date}: {summ.text}",
                summaries)
            )  

def get_documents(opinions: List[Opinion], summaries: List[Summary]) -> List[str]:
    docs = turn_opinions_to_text(opinions) + turn_summaries_to_text(summaries)
    return docs 

async def create_prompt(opinions: List[Opinion], summaries: List[Summary]):
    llm = get_llm() 
    map_chain = LLMChain(llm=llm, prompt=get_template())
    reduce_chain = LLMChain(llm=llm, prompt=get_template())
    combine_chain = StuffDocumentsChain(
            llm_chain=reduce_chain,
            document_variable_name="opinions"
            )
    reduce_documents_chain = ReduceDocumentsChain(
            combine_documents_chain=combine_chain,
            collapse_documents_chain=combine_chain,
            token_max=2000
            )
    map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain,
            reduce_documents_chain=reduce_documents_chain,
            document_variable_name="opinions",
            return_intermediate_steps=False
            )
    docs = get_documents(opinions, summaries)
    spliter = CharacterTextSplitter()
    
    return await map_reduce_chain.arun(spliter.create_documents(docs))
    
