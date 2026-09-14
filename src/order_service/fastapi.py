from fastapi import FastAPI

from order_service.presentation.api.routers import router

app = FastAPI()

app.include_router(router, prefix="/api")