from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import (
    HTMLResponse,
    JSONResponse
)

from config import configs
from database.database import (
    engine,
    Base
)
from api import router

def create_ip_ports_array(ip: str, *ports):
    array = []
    for port in ports:
        array.append(f"{ip}:{str(port)}")
    return array

app = FastAPI(
    title="MDGT Laboratory Test Storage Service",
    description="Сервис для хранения результатов лабораторных испытаний грунтов",
    version="0.1.0")


origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:9573"]

origins += create_ip_ports_array(configs.host_ip, 3000, 8000, 80)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization", "Accept", "X-Requested-With"],
)

app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def index():
    return JSONResponse(content={'massage': 'Hello geology!'}, status_code=200)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)



