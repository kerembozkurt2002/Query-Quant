from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
from backend.config import SQL_REGENERATE_LIMIT
import os

load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)

@tool
def sql_regenerator_agent(prompt:str , data:list, paraphrased_prompt:str, sql_evaluation:str , sql_query:str, number_of_regeneration:int) -> dict[str, str | int]:
    """
    If the previous SQL query was incorrect, it regenerates a new SQL query based on the input prompt, paraphrased prompt, and Excel data.
    """
    if number_of_regeneration< int(SQL_REGENERATE_LIMIT):
        number_of_regeneration += 1
        system_message = SystemMessage(content="""
            You are a SQL Regenerating Agent. 
            If the SQL Evaluation is incorrect then, you have to regenerate a new SQL query based on the input prompt, paraphrased prompt, Excel data, previous wrong SQL Query, and SQL Evaluation.
            """)
        response = llm.invoke([
            system_message,
            HumanMessage(content=f'Prompt:{prompt} \n Paraphrased Prompt: {paraphrased_prompt} \n '
                                 f'Data: {data} \n Wrong SQL Query: {sql_query} \n  SQL Evaluation: {sql_evaluation} '),
        ])
        output = response.content.strip()
        res = {
            "sql_query": output,
            "number_of_regeneration": number_of_regeneration}
        return res
    else:
        return { "sql_query":"LIMIT EXCEEDED", "number_of_regeneration": number_of_regeneration}