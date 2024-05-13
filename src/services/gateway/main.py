from fastapi import FastAPI
from src.model.gateway import HelloResponse
from typing import Dict

app = FastAPI()


@app.get("/{name}")
async def hello(name: str) -> HelloResponse:
   return HelloResponse(name=f"Hello, {name}") 


