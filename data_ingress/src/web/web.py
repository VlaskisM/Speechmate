from fastapi import FastAPI
from src.web.routes.service import router as service_router

app = FastAPI()


app.include_router(service_router)