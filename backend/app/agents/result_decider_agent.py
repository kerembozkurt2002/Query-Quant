from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
import pandas as pd
import pandasql as ps
import re


load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)

@tool
def result_decider_agent(execution_result: pd.DataFrame | str) -> pd.DataFrame |  str:
    """
    Decides the result based on the execution result of the SQL query.
    """
    if isinstance(execution_result, pd.DataFrame):
        if execution_result.empty:
            return "Query executed and no results found"
        else:
            return execution_result
    elif isinstance(execution_result, str) and execution_result=="It is impossible to answer the prompt with the given data.":
        return execution_result
    return "Execution failed. Error: " + str(execution_result)
