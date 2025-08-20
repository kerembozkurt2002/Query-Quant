from typing import TypedDict, Literal, List, Dict, Any, Union
import pandas as pd
from langchain_core.messages import HumanMessage, AIMessage


class AgentState(TypedDict):
    prompt: str | None
    language: str | None
    result: str| None
    excel_data: pd.DataFrame| list | str | None
    paraphrased_prompt: str | None
    sql_query: str | None
    sql_evaluation: str | None
    number_of_regeneration: int
    number_of_executions: int
    execution_result: str | None
    history: List[Union[HumanMessage, AIMessage]] | None
    intent: str | None