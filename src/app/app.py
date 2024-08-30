import os

from fastapi import Depends, FastAPI, Request, HTTPException, status, Response
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from fastapi.security.utils import get_authorization_scheme_param

from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

from config import configs
from database.database import engine, Base
from api import router
from services.depends import get_object_service
from services.object_service import ObjectService


def create_ip_ports_array(ip: str, *ports):
    return [f"{ip}:{port}" for port in ports]


app = FastAPI(
    title="MDGT Laboratory Test Storage Service",
    description="Сервис для хранения результатов лабораторных испытаний грунтов",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:80"
]
origins += create_ip_ports_array(configs.host_ip, 3000, 8000, 80)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_upload_size: int):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request, call_next):
        if request.method == "POST" and request.url.path == "/files/":
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_upload_size:
                return Response("Request entity too large", status_code=413)
        return await call_next(request)

# Добавляем middleware в приложение
app.add_middleware(LimitUploadSizeMiddleware, max_upload_size=50 * 1024 * 1024)  # например, 50MB


app.include_router(router)

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")
app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, objects_service: ObjectService = Depends(get_object_service)):
    authorization = request.cookies.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)

    if token:
        try:
            objects = await objects_service.get_objects()
        except Exception as e:
            objects = []
            # Log the exception if needed

        return templates.TemplateResponse("personal.html",
                                          context={"request": request,
                                                   "objects": objects})
    else:
        return templates.TemplateResponse("index.html", context={"request": request})


@app.on_event("startup")
async def startup_event():
    redis_url = f"redis://{configs.redis_host}:{configs.redis_port}"
    redis_params = {
        "username": configs.redis_user,
        "password": configs.redis_password,
        "encoding": "utf8",
        "decode_responses": True
    }

    redis = aioredis.from_url(redis_url, **redis_params)

    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    async with engine.begin() as conn:
        if configs.mode == 'test':
            await conn.run_sync(Base.metadata.drop_all)

        await conn.run_sync(Base.metadata.create_all)
