# paraphrase_agent.py
from typing import List, Union
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
from backend.app.helper.utils_llm_io import serialize_history, compact_data_preview

load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)

@tool
def paraphrase_agent(prompt: str, intent: str | None,  history: List[Union[HumanMessage, AIMessage]] | None, data: list) -> str:
    """
    Produce a concise, self-contained reformulation the SQL/Result agents can use directly.
    """
    sys = SystemMessage(content="""
You are a Paraphrasing Agent.
- Use the intent and chat history to resolve pronouns like "them/these/that result".
- Refer ONLY to columns that exist in the provided data preview.
- Be specific and executable: include filters, groupings, and measures in plain language.
- If the question cannot be answered with provided columns, return:
  {"rephrased":"", "can_answer_with_data":false, "reason":"<why>"}

Output STRICT JSON:
{"rephrased":"<one sentence>", "can_answer_with_data": true|false, "reason":"<short>"}
""".strip())

    hist = serialize_history(history)
    preview = compact_data_preview(data)

    user = HumanMessage(content=(
        f"CurrentPrompt: {prompt}\n\n"
        f"Intent: {intent}\n\n"
        f"History(JSON): {hist}\n\n"
        f"DataPreview(JSON): {preview}\n"
    ))

    resp = llm.invoke([sys, user])
    return resp.content.strip()
