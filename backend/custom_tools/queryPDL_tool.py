from langchain.llms import OpenAI
from langchain.agents import Tool
from langchain.tools import tool, BaseTool, StructuredTool
from backend.custom_tools.queryPDL import PDLHandler
from typing import Optional, Type, Any, List
from pydantic import BaseModel as PydanticBaseModel, Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)


def multiplier(a: Any, b: Any):
    return int(a) * int(b)


def parsing_multiplier(string):
    string = string.strip()
    try:
        a, b = string.split(",")
    except:
        a, b = string.split("and")
    return multiplier(int(a), int(b))


class CalculatorInput(PydanticBaseModel):
    # question: str = Field(description="should be in thee calculator query")
    # power: int = Field
    a: str
    b: str


class ParsingMultiplierTool(BaseTool):
    name = "Multiplier"
    description = "Useful for when you need to multiply two numbers together. "
    "Use this tool if the question is about multiplying two numbers. "
    "The input to this tool should be two integers. "
    "representing the two numbers you want to multiply together. "
    "For example, 1,2 should be the input if you wanted to multiply 1 by 2."

    return_direct = True
    args_schema: Type[PydanticBaseModel] = CalculatorInput

    def _run(
        self, a: str, b: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool"""
        print(f"\nInput numbers: {a}, {b}")
        return multiplier(a, b)

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")


class PDLHandlerInput(PydanticBaseModel):
    skills: Optional[str] = Field(description="Skills that a candidate has")
    location_country: Optional[str] = Field(
        description="current location country of the candidate"
    )
    companies: Optional[str] = Field(
        description="Name of companies that a candidate has worked at"
    )


def parseStringToList(string):
    string = string.strip()
    separators = [",", ";", "!"]
    values = []
    max_len = 0
    for separator in separators:
        print(f"Separator: {separator}")
        list_of_strs = string.split(separator)
        if len(list_of_strs) > max_len:
            max_len = len(list_of_strs)
            values = list_of_strs

    values = [x.strip() for x in values]
    return values


def execPDLQuery(**kwargs):
    """
    Given input strings such as:
        `
            skills: str
            location_country: str
            companies: str

        `
    execute a PDL query
    """
    must_clauses = []
    should_clauses = []
    print(f"========================\n Keys and values input to the TOOL:")
    for key, str_of_values in kwargs.items():
        print(f"{key}: {str_of_values}")
        if str_of_values is not None and len(str_of_values) > 0:
            values = parseStringToList(str_of_values)
            clauses = [{"match": {key: val}} for val in values]
            # TODO: separate must and should
            must_clauses.extend(clauses)
    # TODO: handle different searches to make sure thare are always responses
    query = PDLHandler.buildQuery(must_clauses, should_clauses)
    print(f"QUERY: {query}")
    success, response = PDLHandler.sendQuery(query, 1)
    return PDLHandler.convertResponseToStringOfProfiles(response)


class PDLHandlerTool(BaseTool):
    name = "PDLHandlerTool"
    description = "Useful for when you need to find candidates/applicants for hiring. "

    return_direct = True
    args_schema: Type[PydanticBaseModel] = PDLHandlerInput

    def _run(
        self,
        skills: Optional[str] = None,
        location_country: Optional[str] = None,
        companies: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool"""
        if skills is not None:
            print(f"\n=> Input skills: {skills}")
        if location_country is not None:
            print(f"\n=> Input location_country: {location_country}")
        if companies is not None:
            print(f"\n=> Input companies: {companies}")
        kwargs = {
            "skills": skills,
            "location_country": location_country,
            "experience.company.name": companies,
        }
        return execPDLQuery(**kwargs)

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")


if __name__ == "__main__":
    print(ParsingMultiplierTool.description)
