from backend.app.agents.language_agent import detect_language_agent
from backend.app.workflow.agent_state import AgentState
from backend.app.agents.paraphrasize_agent import paraphrase_agent
from backend.app.agents.sql_generator_agent import sql_generator_agent
from backend.app.agents.sql_executor_agent import sql_executor_agent
from backend.app.agents.sql_regenerate_agent import sql_regenerator_agent
from backend.app.agents.sql_evaluator_agent import sql_evaluator_agent
from backend.app.agents.result_decider_agent import  result_decider_agent
from backend.app.agents.result_agent import result_agent
import pandas as pd

def test_detect_language_node():
    state = AgentState(prompt="What is the capital of France?")
    output = detect_language_agent.invoke(state)
    return output

def test_paraphrase_prompt_node():
    state = AgentState(prompt="What is the capital of France?", excel_data=[{"Country": "France", "Capital": "Paris"}])
    output = paraphrase_agent.invoke({"prompt": state["prompt"], "data": state["excel_data"]})
    return output

def test_sql_generating_node():
    state = AgentState(prompt="What is the capital of France?", excel_data=[{"Country": "France", "Capital": "Paris"}], paraphrased_prompt="What is the capital city of France?")
    output = sql_generator_agent.invoke({"prompt": state["prompt"], "data": state["excel_data"], "paraphrased_prompt": state["paraphrased_prompt"]})
    return output

def test_sql_evaluating_node():
    state = AgentState(prompt="What is the capital of France?", excel_data=[{"Country": "France", "Capital": "Paris"}], paraphrased_prompt="What is the capital city of France?", sql_query="SELECT Capital FROM data WHERE Country = 'France'")
    output = sql_evaluator_agent.invoke({"prompt": state["prompt"], "data": state["excel_data"], "paraphrased_prompt": state["paraphrased_prompt"], "sql_query": state["sql_query"]})
    return output

def test_sql_regeneration_node():
    state = AgentState(prompt="What is the capital of France?", excel_data=[{"Country": "France", "Capital": "Paris"}], paraphrased_prompt="What is the capital city of France?", sql_query="SELECT Capital FROM data WHERE Country = 'France'", number_of_regeneration=0, sql_evaluation="SQL query is valid")
    output = sql_regenerator_agent.invoke({"prompt": state["prompt"], "data": state["excel_data"], "paraphrased_prompt": state["paraphrased_prompt"], "sql_query": state["sql_query"], "number_of_regeneration": state["number_of_regeneration"], "sql_evaluation": state["sql_evaluation"]})
    return output

def test_sql_execution_node():
    state = AgentState(prompt="What is the capital of France?", excel_data=[{"Country": "France", "Capital": "Paris"}], paraphrased_prompt="What is the capital city of France?", sql_query="SELECT Capital FROM data WHERE Country = 'France'", sql_evaluation="Correct")
    output = sql_executor_agent.invoke({"data": state["excel_data"], "sql_evaluation": state["sql_evaluation"], "sql_query": state["sql_query"]})
    return output

def test_result_decision_node():
    state = AgentState(prompt="What is the capital of France?", excel_data=[{"Country": "France", "Capital": "Paris"}], paraphrased_prompt="What is the capital city of France?", sql_query="SELECT Capital FROM data WHERE Country = 'France'", sql_evaluation="Correct", execution_result=pd.DataFrame([{"Capital": "Paris"}]))
    output = result_decider_agent.invoke({"prompt": state["prompt"], "data": state["excel_data"], "paraphrased_prompt": state["paraphrased_prompt"], "sql_query": state["sql_query"], "sql_evaluation": state["sql_evaluation"], "execution_result": state["execution_result"]})
    return output

def test_result_node():
    state = AgentState(prompt="What is the capital of France?", excel_data=[{"Country": "France", "Capital": "Paris"}], paraphrased_prompt="What is the capital city of France?", sql_query="SELECT Capital FROM data WHERE Country = 'France'", sql_evaluation="Correct", execution_result=pd.DataFrame([{"Capital": "Paris"}]), result=pd.DataFrame([{"Capital": "Paris"}]))
    output = result_agent.invoke({"prompt": state["prompt"], "data": state["excel_data"], "paraphrased_prompt": state["paraphrased_prompt"], "sql_query": state["sql_query"], "sql_evaluation": state["sql_evaluation"], "execution_result": state["execution_result"], "result": state["result"]})
    return output

def run_all_tests():
    print("Testing detect_language_node...")
    print(test_detect_language_node())

    print("\nTesting paraphrase_prompt_node...")
    print(test_paraphrase_prompt_node())

    print("\nTesting sql_generating_node...")
    print(test_sql_generating_node())

    print("\nTesting sql_evaluating_node...")
    print(test_sql_evaluating_node())

    print("\nTesting sql_regeneration_node...")
    print(test_sql_regeneration_node())

    print("\nTesting sql_execution_node...")
    print(test_sql_execution_node())

    print("\nTesting result_decision_node...")
    print(test_result_decision_node())

    print("\nTesting result_node...")
    print(test_result_node())

if __name__ == "__main__":
    run_all_tests()