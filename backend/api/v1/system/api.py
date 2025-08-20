from fastapi import APIRouter, Response

system_router = APIRouter()

@system_router.get("/v1/api/healthcheck")
async def healthcheck():
    return Response(content="OK", status_code=200)