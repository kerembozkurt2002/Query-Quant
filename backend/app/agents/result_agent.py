from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
import pandas as pd
import pandasql as ps
import re
from backend.app.agents.chart_generator_agent import chart_generator_agent


load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)

@tool
def result_agent(prompt:str ,result: pd.DataFrame | str , language:str, execution_result:pd.DataFrame| str) -> pd.DataFrame |  str:
    """
    Processes the execution result and generates charts if requested.
    """
    system_message = SystemMessage(content="""
            You are a Result Agent.
            Your task is writing a text response based on the execution result of the SQL query.
            Language of the response should be in that language: {language}.            
    """)
    response = llm.invoke([
        system_message,
        HumanMessage(
            content=f'Prompt: {prompt} \n Language{language}: \n Execution Result: {result} \n'),
    ])
    response_text = response.content.strip()

    if isinstance(execution_result, pd.DataFrame):
        execution_result = execution_result.to_dict('records')

    if isinstance(result, pd.DataFrame):
        chart_keywords = ['chart', 'graph', 'plot', 'pie', 'bar', 'line', 'scatter', 'visualization']
        prompt_lower = prompt.lower()
        
        if any(keyword in prompt_lower for keyword in chart_keywords):
            chart_result = chart_generator_agent.invoke({"prompt": prompt, "data": result})
            
            if chart_result["status"] == "success":
                return {
                    "status": "success",
                    "data": chart_result["data"],
                    "chart_image": chart_result["chart_image"],
                    "chart_type": chart_result["chart_type"],
                    "message": chart_result["message"],
                    "response_text": response_text,
                    "execution_result": execution_result
                }
            else:
                return {
                    "status": "success",
                    "data": chart_result["data"],
                    "message": "Query executed successfully, but chart generation failed",
                    "response_text": response_text,
                    "execution_result": execution_result

                }
        else:
            data = result.to_dict("records")
            return {
                "status": "success",
                "data": data,
                "message": "Query executed successfully",
                "response_text": response_text,
                "execution_result": execution_result
            }
    else:
        if result == "Query executed and no results found":
            return {
                "status": "success",
                "data": None,
                "message": "Query executed and no results found",
                "response_text": response_text,
                "execution_result": execution_result
            }
        elif result == "It is impossible to answer the prompt with the given data.":
            return {
                "status": "success",
                "data": None,
                "message": "It is impossible to answer the prompt with the given data.",
                "response_text": response_text,
                "execution_result": "It is impossible to answer the prompt with the given data."
            }
        else:
            return {
                "status": "error",
                "data": None,
                "message": f"Execution failed. Error: {str(result)}",
                "response_text": "Execution failed. Error: " + str(result),
                "execution_result": "Execution failed. Error: " + str(result)
            }
