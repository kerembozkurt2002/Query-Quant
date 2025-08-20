from uvicorn import run
from backend.app.server import create_app
from backend.config import HOST ,PORT , OPENAI_API_KEY
from backend.app.workflow.agent_state import AgentState
from backend.app.workflow.overflow import workflow
import pandas as pd
import json

app = create_app()

if __name__ == '__main__':
    run("main:app", host=HOST, port=PORT, reload=True)

    with open("graph.png", "wb") as f:
        f.write(workflow.get_graph().draw_mermaid_png())



