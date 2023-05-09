from __future__ import annotations
import os
import sys
from io import StringIO

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.agents import load_tools
from langchain.llms import OpenAI
from pydantic import BaseModel
from backend.custom_tools.queryPDL_tool import PDLHandlerTool
from typing import Dict
import uvicorn
import os

load_dotenv()


class Question(BaseModel):
    question: str


app = FastAPI()


@app.post("/ask")
def ask(question: Question) -> Dict[str, str]:
    llm = OpenAI(temperature=0)
    tools = [PDLHandlerTool()]

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    # The following used to turn off the console printing
    # backup = sys.stdout
    # try:
    #     sys.stdout = StringIO()
    #     answer = agent.run(question)
    #     # answer = sys.stdout.getvalue()
    #     return {"result": answer}
    # finally:
    #     sys.stdout.close()
    #     sys.stdout = backup
    answer = agent.run(question)
    return {"result": answer}


@app.get("/")
def home():
    return "Hello streamlit-fastapi-langchain backend!"


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=int(os.environ["BACKEND_PORT"]))
