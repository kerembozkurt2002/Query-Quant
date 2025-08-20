from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
import pandas as pd
from backend.app.workflow.agent_state import AgentState

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

@tool
def sql_evaluator_agent(prompt:str , data:list, paraphrased_prompt:str, sql_query:str) -> str:
    """
    Evaluates the generated SQL query based on the input prompt, paraphrased prompt, and Excel data.
    """

    system_message = SystemMessage(content="""
        You are a SQL Evaluator Agent.
        Your job is to carefully analyze whether the provided SQL query matches the requirements described in the paraphrased prompt.
        
        EVALUATION CRITERIA:
        1. The SQL query must be syntactically valid and executable
        2. The SQL query must use the correct table name 'data'
        3. The SQL query must directly answer the prompt requirements
        4. The SQL query must use only columns that exist in the data
        5. The SQL query must be compatible with pandasql syntax
        
        RESPONSE FORMAT:
        - Only respond with "Correct" if ALL criteria are met
        - Otherwise, respond with "Incorrect: <brief explanation>"
        - Do NOT include any extra text or explanations
    """)
    response = llm.invoke([
        system_message,
        HumanMessage(content=f'Prompt:{prompt} \n Paraphrased Prompt: {paraphrased_prompt} \n Data: {data} \n SQL Query: {sql_query}'),
    ])
    output = response.content.strip()
    return output
