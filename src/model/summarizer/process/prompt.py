import json
from typing import Any, Dict, List, Tuple

from src.model.opinions.opinion import Opinion
from src.model.summarizer.summary import Summary
from langchain_core.prompts import PromptTemplate 
from langchain.chains.llm import LLMChain
from langchain_google_vertexai.llms import VertexAI
import google.auth as auth

llm: VertexAI | None = None

def get_cred(private_key: str, private_key_id: str) -> Dict:
    return {
            "type": "service_account",
            "project_id": "chefcito-comidas",
            "private_key_id": private_key_id,
            "private_key": private_key,
            "client_email": "summarizer-service@chefcito-comidas.iam.gserviceaccount.com",
            "client_id": "100286983511312951818",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/summarizer-service%40chefcito-comidas.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
            }

def init_google(private_key: str, private_key_id: str) -> Tuple[Any, str | None]:
    cred = get_cred(private_key, private_key_id) 
    return auth.load_credentials_from_dict(cred)

def init(private_key: str, private_key_id: str, model: str = 'text-bison'):
    global llm
    creds, project = init_google(private_key, private_key_id)
    llm = VertexAI(
            project=project,
            model_name=model,
            credentials=creds
            )

def get_template() -> PromptTemplate:
    map_template = """The following is a set of opinions
    {opinions}
    Based on this list of opinions, please generate a summarized
    opinion:
    """
    return PromptTemplate.from_template(map_template)


def get_llm() -> VertexAI:
    global llm
    if llm == None:
        raise Exception("Prompt model not yet initialized")
    return llm
    

def create_prompt(opinions: List[Opinion], summaries: List[Summary]):
    llm = get_llm() 
    chain = LLMChain(llm=llm, prompt=get_template())
    
