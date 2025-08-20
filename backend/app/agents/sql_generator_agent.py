from typing import List, Union

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
import pandas as pd
from backend.app.workflow.agent_state import AgentState

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

@tool
def sql_generator_agent(prompt:str , data:list, paraphrased_prompt:str , history:List[Union[HumanMessage, AIMessage]] ) -> str:
    """
    Generates SQL queries based on the input prompt, paraphrased prompt, and Excel data.
    Uses chat history for context
    """
    system_message = SystemMessage(content="""
        You are a SQL Generating Agent. 
        You have to produce valid SQL queries using the context of prompt, paraphrased prompt, and Excel rows.
        READ THE CHAT HISTORY MESSAGES PROVIDED TO YOU.
        
        IMPORTANT RULES:
        1. Return ONLY the SQL query, no explanations or additional text
        2. Use the table name 'data' for the dataset
        3. Make sure the SQL is syntactically correct and executable
        4. Use proper SQL syntax with pandasql compatibility
        5. Do not include markdown formatting or code blocks
        6. The query should directly answer the prompt using the available data columns
        7. If the prompt is impossible to answer with the given data, return "Impossible"
        8. Use the previous conversation context to understand references like "them", "those", etc.

    """)

    response = llm.invoke([
        system_message,
        HumanMessage(content=f'Prompt:{prompt} \n Paraphrased Prompt: {paraphrased_prompt} \n Data: {data} \n History: {history}'),
    ])
    output = response.content.strip()
    return output
