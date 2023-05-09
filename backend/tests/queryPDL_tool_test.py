from langchain.llms import OpenAI
from backend.custom_tools.queryPDL_tool import ParsingMultiplierTool, PDLHandlerTool
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from dotenv import load_dotenv
import os

load_dotenv()
OpenAI.openai_api_key = os.environ["OPENAI_API_KEY"]


def testSImpleMultiplier():
    llm = OpenAI(temperature=0)
    tools = [ParsingMultiplierTool()]

    mrkl = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    response = mrkl.run("What is the multiplication of 10 and 20")
    print(f"===========================")
    print(f"{response}")


def testFindingCandidates(question: str = None):
    llm = OpenAI(temperature=0)
    tools = [PDLHandlerTool()]

    mrkl = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    if question is None:
        question = "Find an engineer in Vietnam skilled in python and java"
    response = mrkl.run(question)
    print(f"===========================")
    print(f"{response}")


if __name__ == "__main__":
    testFindingCandidates()
