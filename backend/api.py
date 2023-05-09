from __future__ import annotations
import os

os.environ["LANGCHAIN_TRACING"] = "true"
os.environ["LANGCHAIN_SESSION"] = "streamlit-langchain-backend"
os.environ["LANGCHAIN_HANDLER"] = "langchain"


import sys
from io import StringIO

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.agents import load_tools
from langchain.llms import OpenAI
from pydantic import BaseModel
import uvicorn
import os

load_dotenv()


class Question(BaseModel):
    question: str


app = FastAPI()


@app.post("/ask")
def ask(question: Question) -> dict[str, str]:
    llm = OpenAI(temperature=0)
    tools = load_tools(["llm-math"], llm=llm)
    agent = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )
    backup = sys.stdout
    try:
        sys.stdout = StringIO()
        agent.run(question)
        answer = sys.stdout.getvalue()
    finally:
        sys.stdout.close()
        sys.stdout = backup
    return {"result": answer}


@app.get("/")
def home():
    return "Hello streamlit-fastapi-langchain backend!"


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=int(os.environ["PORT"]))
