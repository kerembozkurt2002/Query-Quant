from fastapi import FastAPI
from backend.api.v1 import v1_router

def create_app():
    app = FastAPI(title="Query-Quant FastAPI")
    app.include_router(v1_router)
    return app

