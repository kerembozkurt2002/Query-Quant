import pandas as pd
from langgraph.graph import StateGraph
from backend.app.agents.language_agent import detect_language_agent
from backend.app.workflow.agent_state import AgentState
from langchain_openai import ChatOpenAI
from backend.app.agents.paraphrasize_agent import paraphrase_agent
from backend.app.agents.sql_generator_agent import sql_generator_agent
from backend.app.agents.sql_executor_agent import sql_executor_agent
from backend.app.agents.sql_regenerate_agent import sql_regenerator_agent
from backend.app.agents.sql_evaluator_agent import sql_evaluator_agent
from backend.app.agents.result_decider_agent import  result_decider_agent
from backend.app.agents.result_agent import result_agent
from backend.app.agents.analyze_history_agent import analyze_history_agent
from backend.config import SQL_EXECUTION_LIMIT , SQL_REGENERATE_LIMIT

llm = ChatOpenAI(model="gpt-4o", temperature=0)


def detect_language_node(state: AgentState) -> AgentState:
    language = detect_language_agent.invoke(state['prompt'])
    state['language'] = language
    state['intent'] = ""
    return state

def analyze_history_node(state: AgentState) -> AgentState:
    row_data = state["excel_data"].to_dict('records')
    response = analyze_history_agent.invoke({"prompt":state["prompt"], "history": state["history"], "data" : row_data})
    print("Intent: ", response)
    state["intent"] = response
    return state

def paraphrase_prompt_node(state: AgentState) -> AgentState:
    row_data = state["excel_data"].to_dict('records')
    response = paraphrase_agent.invoke({"prompt":state["prompt"], "intent":state["intent"], "history":state["history"] , "data" : row_data})
    state["paraphrased_prompt"] = response
    state["excel_data"]=row_data
    return state

def sql_generating_node(state: AgentState) -> AgentState:
    response = sql_generator_agent.invoke({"prompt":state["prompt"], "data" : state["excel_data"] , "paraphrased_prompt": state["paraphrased_prompt"] , "history": state["history"]})
    state["sql_query"] = response
    if response == "Impossible":
        state["execution_result"] = "It is impossible to answer the prompt with the given data."
    state["number_of_regeneration"] = 0
    state["number_of_executions"]= 0
    return state

def sql_evaluating_node(state: AgentState) -> AgentState:
    response = sql_evaluator_agent.invoke({"prompt":state["prompt"], "data" : state["excel_data"] , "paraphrased_prompt": state["paraphrased_prompt"] , "sql_query": state["sql_query"]})
    state["sql_evaluation"] = response
    return state

def sql_regeneration_node(state: AgentState) -> AgentState:
    response = sql_regenerator_agent.invoke({"prompt":state["prompt"], "data" : state["excel_data"] , "paraphrased_prompt": state["paraphrased_prompt"] , "sql_query": state["sql_query"] , "number_of_regeneration": state["number_of_regeneration"], "sql_evaluation": state["sql_evaluation"]})
    state["number_of_regeneration"] +=1
    state["sql_query"] = response["sql_query"]
    return state

def sql_execution_node(state: AgentState) -> AgentState:
    response = sql_executor_agent.invoke(
        { "data": state["excel_data"], "sql_evaluation": state["sql_evaluation"], "sql_query": state["sql_query"]})
    state["execution_result"] = response
    state["number_of_executions"] += 1
    state["number_of_regeneration"] = 0
    return state

def result_decision_node(state: AgentState) -> AgentState:
    response = result_decider_agent.invoke(
        { "execution_result": state["execution_result"]})
    state["result"] = response
    return state

def result_agent_node(state: AgentState) -> AgentState:
    response = result_agent.invoke(
        {"prompt":state["prompt"], "result": state["result"],
         "language": state["language"], "execution_result": state["execution_result"]})
    state["result"] = response
    return state

def generation_decider(state: AgentState) -> str:
    if state["sql_query"] == "Impossible":
        return "result_decider"
    else:
        return "sql_evaluate"

def history_decider(state: AgentState) -> str:
    if state["history"] is None or len(state["history"]) == 0:
        return "paraphrase_prompt"
    else:
        return "analyze_history"

def evaluation_decider(state: AgentState) -> str:
    num_of_regen = state["number_of_regeneration"]
    if state["sql_evaluation"] == "Correct":
        return "sql_execute"
    else:
        if num_of_regen > SQL_REGENERATE_LIMIT:
            return "sql_execute"
        elif state["number_of_executions"] > SQL_EXECUTION_LIMIT:
            state["sql_query"] = "LIMIT EXCEEDED"
            return "sql_execute"
        else:
            return "sql_regenerate"

def execution_decider(state: AgentState) -> str:
    num_of_exec = state["number_of_executions"]
    if isinstance(state["execution_result"], pd.DataFrame) :
        return "result_decider"
    elif isinstance(state["execution_result"], str) and num_of_exec >= SQL_EXECUTION_LIMIT:
        return "result_decider"
    elif isinstance(state["execution_result"], str) and state["execution_result"] == "Incorrect" and state["number_of_regeneration"] < SQL_REGENERATE_LIMIT:
        return "sql_regenerate"
    else:
        return "result_decider"

graph = StateGraph(AgentState)
graph.add_node("detect_language", detect_language_node)
graph.add_node("paraphrase_prompt", paraphrase_prompt_node)
graph.add_node("sql_generate", sql_generating_node)
graph.add_node("sql_evaluate", sql_evaluating_node)
graph.add_node("sql_regenerate", sql_regeneration_node)
graph.add_node("sql_execute", sql_execution_node)
graph.add_node("result_decider", result_decision_node)
graph.add_node("result_agent", result_agent_node)
graph.add_node("analyze_history", analyze_history_node)

graph.set_entry_point("detect_language")
graph.add_conditional_edges(
    "detect_language",
    history_decider,
    {
        "analyze_history": "analyze_history",
        "paraphrase_prompt": "paraphrase_prompt"
    }
)
graph.add_edge("analyze_history", "paraphrase_prompt")
graph.add_edge("paraphrase_prompt", "sql_generate")
graph.add_conditional_edges(
    "sql_generate",
        generation_decider,
            {
                "result_decider": "result_decider",
                "sql_evaluate": "sql_evaluate",
            }
)

graph.add_conditional_edges(
    "sql_evaluate",
    evaluation_decider,
    {
        "sql_execute": "sql_execute",
        "sql_regenerate": "sql_regenerate"
    }
)
graph.add_edge("sql_regenerate", "sql_evaluate")
graph.add_conditional_edges(
    "sql_execute",
    execution_decider,
    {
        "result_decider": "result_decider",
        "sql_regenerate": "sql_regenerate"
    }
)

graph.add_edge("result_decider", "result_agent")
graph.set_finish_point("result_agent")


workflow = graph.compile()

