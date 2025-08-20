from fastapi import APIRouter
from .api import system_router

api_system_router = APIRouter()
api_system_router.include_router(system_router)

__all__ = ["api_system_router"]