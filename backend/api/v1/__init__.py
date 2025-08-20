from fastapi import APIRouter
from .system import api_system_router
from .document import api_document_router

v1_router=APIRouter()
v1_router.include_router(api_system_router, prefix="/system", tags=["System API"])
v1_router.include_router(api_document_router, prefix="/document", tags=["Document API"])