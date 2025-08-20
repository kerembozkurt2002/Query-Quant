# analyze_history_agent.py
from typing import List, Union
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
from backend.app.helper.utils_llm_io import serialize_history, compact_data_preview

load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)

@tool
def analyze_history_agent(prompt: str, history: List[Union[HumanMessage, AIMessage]] | None, data: list) -> str:
    """
    Analyze chat history + data headers to resolve references (e.g., 'them', 'these'),
    decide what the user actually wants *now*, and emit a strict JSON plan.
    """
    sys = SystemMessage(content="""
You are an Analysis Agent that resolves context from prior messages and the current prompt.
Goals:
- Understand what the user wants *now*.
- Resolve anaphora like "them/these/that result" by looking at the most recent assistant outputs.
- Use only the provided data columns. Do not invent columns.
- If the current question cannot be answered with the provided columns, say so.

Output STRICT JSON with keys:
{
  "resolved_question": "<one-sentence reformulation, concrete and self-contained>",
  "uses_previous_result": true|false,
  "referenced_columns": ["ColA", "ColB", ...],   // subset of available columns
  "filters": [{"column":"ColX","op":"=","value":"..."}],  // optional
  "aggregation": {"group_by":["ColY"], "metrics":[{"op":"COUNT","column":"*"}]}, // optional
  "chart": {"type":"pie|bar|line|none"},         // best-guess for visualization, or "none"
  "can_answer_with_data": true|false,
  "reason": "<short reason>"
}

Rules:
- NEVER output anything but a single JSON object.
- If unsure, set can_answer_with_data=false and explain briefly in 'reason'.
""".strip())

    hist = serialize_history(history)
    preview = compact_data_preview(data)

    user = HumanMessage(content=(
        f"CurrentPrompt: {prompt}\n\n"
        f"History(JSON): {hist}\n\n"
        f"DataPreview(JSON): {preview}\n"
    ))

    resp = llm.invoke([sys, user])
    return resp.content.strip()
