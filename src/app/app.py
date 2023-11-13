import os

from fastapi import FastAPI, Request, HTTPException, status
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import (
    HTMLResponse,
    JSONResponse
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from fastapi.security.utils import get_authorization_scheme_param

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
    version="0.9.1")


origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:80"
]

origins += create_ip_ports_array(configs.host_ip, 3000, 8000, 80)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], #["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["*"], #["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   #"Authorization", "Accept", "X-Requested-With"],
)

app.include_router(router)

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")
app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        authorization: str = request.cookies.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        if token:
            return templates.TemplateResponse("personal.html", context={"request": request})
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials',
                headers={'Authenticate': 'Bearer'})
    except HTTPException:
        return templates.TemplateResponse("index.html", context={"request": request})

@app.on_event("startup")
async def startup_event():
    if configs.mode == 'test':
        redis = aioredis.from_url(
            "redis://localhost:6379",
            encoding="utf8", decode_responses=True)
    else:
        redis = aioredis.from_url(
            f"redis://{configs.redis_host}:{configs.redis_port}",
            username=configs.redis_user, password=configs.redis_password,
            encoding="utf8", decode_responses=True)

    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    async with engine.begin() as conn:
        if configs.mode == 'test':
            await conn.run_sync(Base.metadata.drop_all)

        await conn.run_sync(Base.metadata.create_all)



