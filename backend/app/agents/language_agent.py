from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

@tool
def detect_language_agent(prompt: str) -> str:
    """
    Detects the language of the input text using a language detection agent.
    """
    system_message = SystemMessage(content=f"""
        You are a language detection agent. 
        Your task is to determine the language of the input text.
        The input will be a user message, and you should respond with the name of the language in lowercase.
    """)

    response = llm.invoke([
        system_message,
        HumanMessage(content=prompt)
    ])
    language = response.content.strip().lower()
    return language


