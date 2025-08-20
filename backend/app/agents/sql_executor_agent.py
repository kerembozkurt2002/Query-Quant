from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
import pandas as pd
import pandasql as ps
import re
from backend.app.helper.utils_llm_io import extract_sql, looks_like_sql



load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def clean_sql(sql_query: str) -> str:
    return extract_sql(sql_query)

@tool
def sql_executor_agent(data:list, sql_evaluation:str , sql_query:str) -> str:
    """
    Executes the SQL query against the provided data if the evaluation is correct.
    """
    if sql_evaluation != "Correct":
        return "Incorrect"

    try:
        df_data = pd.DataFrame(data)
        cleaned_sql = clean_sql(sql_query)

        if not looks_like_sql(cleaned_sql):
            return f"Incorrect: Model did not return a SQL query. Got: {cleaned_sql[:120]}"

        print(f"Executing SQL: {cleaned_sql}")
        print(f"Data columns: {list(df_data.columns)}")
        output = ps.sqldf(cleaned_sql, {"data": df_data})
        return output
    except Exception as e:
        print(f"SQL execution error: {str(e)}")
        return f"Incorrect: {str(e)}"
