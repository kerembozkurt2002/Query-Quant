from fastapi import APIRouter
from .api import document_router

api_document_router = APIRouter()
api_document_router.include_router(document_router)

__all__ = ["api_document_router"]