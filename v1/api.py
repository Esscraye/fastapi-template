from fastapi import APIRouter
from v1.endpoints.endpoint import router as user_router

api_router = APIRouter()
api_router.include_router(user_router)