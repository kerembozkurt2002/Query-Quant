from fastapi import APIRouter, HTTPException, Response , File , UploadFile
import pandas as pd
import json
from langchain_core.messages import HumanMessage, AIMessage
from backend.app.workflow.overflow import workflow

document_router = APIRouter()

@document_router.get("/v1/api/healthcheck")
async def healthcheck():
    return Response(content="OK", status_code=200)

@document_router.post("/v1/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        return  HTTPException(status_code=400, detail="Unsupported file type. Only .xlsx, .xls, and .csv files are allowed.")

    try:
        if file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file.file)
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        else:
            return HTTPException(status_code=400, detail="Unsupported file type. Only .xlsx, .xls, and .csv files are allowed.")

        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def upload_file_prompt(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        return  HTTPException(status_code=400, detail="Unsupported file type. Only .xlsx, .xls, and .csv files are allowed.")

    try:
        if file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file.file)
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        else:
            return HTTPException(status_code=400, detail="Unsupported file type. Only .xlsx, .xls, and .csv files are allowed.")

        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def parse_history(history_json: str | None):
    if not history_json:
        return []
    raw = json.loads(history_json)
    msgs = []
    for m in raw:
        type, content = m.get("type"), m.get("content", "")
        if type == "human":
            msgs.append(HumanMessage(content=content))
        elif type == "ai":
            msgs.append(AIMessage(content=content))
    return msgs

@document_router.post("/v1/api/prompt")
async def process_prompt(
    prompt: str,
    file: UploadFile = File(...),
    history: str | None = None
):
    excel_data = await upload_file_prompt(file)
    hist_list = parse_history(history)

    try:
        result = workflow.invoke({"prompt": prompt,
                                  "excel_data": excel_data,
                                  "history": hist_list
                                  })
        return result["result"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

