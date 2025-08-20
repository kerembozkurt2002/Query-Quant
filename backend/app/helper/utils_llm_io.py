from typing import List, Union
from langchain_core.messages import HumanMessage, AIMessage
import re

def serialize_history(history: List[Union[HumanMessage, AIMessage]], keep_last: int = 8) -> list[dict]:
    """
    Convert LangChain messages to a compact, model-friendly list of dicts.
    Keeps the last N messages to control token use.
    """
    if not history:
        return []
    trimmed = history[-keep_last:]
    out = []
    for m in trimmed:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        content = m.content if isinstance(m.content, str) else str(m.content)
        if len(content) > 2000:
            content = content[:2000] + " …[truncated]"
        out.append({"role": role, "content": content})
    return out

def compact_data_preview(data: list, max_rows: int = 3) -> dict:
    """
    Expect `data` as list[dict]. Return only headers and a few sample rows.
    """
    if not data:
        return {"columns": [], "sample_rows": []}
    columns = list(data[0].keys())
    sample_rows = data[:max_rows]
    return {"columns": columns, "sample_rows": sample_rows}


_SQL_START = re.compile(r'(?is)^\s*(select|with|insert|update|delete|create|drop|pragma)\b')

def extract_sql(text: str) -> str:
    m = re.search(r"```(?:sql)?\s*(.*?)```", text, flags=re.S|re.I)
    candidate = m.group(1).strip() if m else text.strip()

    m2 = re.search(r'(?is)\b(select|with|insert|update|delete|create|drop|pragma)\b', candidate)
    if m2:
        candidate = candidate[m2.start():]

    candidate = candidate.split(';')[0].strip()
    return candidate

def looks_like_sql(text: str) -> bool:
    return bool(_SQL_START.match(text or ""))
