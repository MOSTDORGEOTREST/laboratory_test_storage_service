"""
LTS Admin — панель управления лабораториями.

Создаёт изолированные инстансы LTS (база в общем Postgres-кластере +
контейнер web с метками Traefik) через веб-интерфейс.
Авторизация: один админ из env (ADMIN_USERNAME / ADMIN_PASSWORD),
JWT в httponly-куке — так же, как в основном приложении.
"""

import os
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, JWTError
from pydantic import BaseModel, Field

from provision import Config, ProvisionError, make_provisioner, validate_name

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
JWT_SECRET = os.environ.get("ADMIN_JWT_SECRET")
JWT_ALGORITHM = "HS256"
TOKEN_TTL_HOURS = int(os.environ.get("ADMIN_TOKEN_TTL_HOURS", "12"))

if not ADMIN_PASSWORD or not JWT_SECRET:
    if os.environ.get("ADMIN_MOCK"):
        ADMIN_PASSWORD = ADMIN_PASSWORD or "admin"
        JWT_SECRET = JWT_SECRET or "mock-secret"
    else:
        raise RuntimeError("ADMIN_PASSWORD и ADMIN_JWT_SECRET обязательны (см. README)")

cfg = Config()
provisioner = make_provisioner(cfg)

app = FastAPI(title="LTS Admin", docs_url=None, redoc_url=None)

BASE_DIR = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# ---------- Auth ----------

exception_auth = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")


def current_admin(request: Request) -> str:
    authorization = request.cookies.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization or "")
    if scheme.lower() != "bearer" or not token:
        raise exception_auth
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise exception_auth from None
    if payload.get("sub") != ADMIN_USERNAME:
        raise exception_auth
    return ADMIN_USERNAME


class LoginData(BaseModel):
    username: str
    password: str


@app.post("/api/login")
async def login(data: LoginData):
    import secrets as _secrets
    ok = _secrets.compare_digest(data.username, ADMIN_USERNAME) and \
        _secrets.compare_digest(data.password, ADMIN_PASSWORD)
    if not ok:
        raise exception_auth
    now = datetime.utcnow()
    token = jwt.encode(
        {"sub": ADMIN_USERNAME, "iat": now, "exp": now + timedelta(hours=TOKEN_TTL_HOURS)},
        JWT_SECRET, algorithm=JWT_ALGORITHM,
    )
    response = JSONResponse({"message": "ok"})
    response.set_cookie("Authorization", f"Bearer {token}", httponly=True, samesite="lax")
    return response


@app.get("/api/logout")
async def logout():
    response = JSONResponse({"message": "ok"})
    response.delete_cookie("Authorization")
    return response


@app.get("/api/me")
async def me(admin: str = Depends(current_admin)):
    return {"username": admin, "domain": cfg.domain, "image": cfg.lts_image,
            "mock": cfg.mock}


# ---------- Лаборатории ----------

class LabCreate(BaseModel):
    name: str = Field(..., max_length=20)
    display_name: str = Field(..., max_length=100)


def _provision_error(err: ProvisionError):
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))


@app.get("/api/labs")
async def list_labs(admin: str = Depends(current_admin)):
    return await provisioner.list_labs()


@app.get("/api/labs/check")
async def check_name(name: str, admin: str = Depends(current_admin)):
    error = validate_name(name)
    if error:
        return {"ok": False, "reason": error}
    if await provisioner.name_taken(name):
        return {"ok": False, "reason": "Имя уже занято"}
    return {"ok": True, "url": f"{cfg.scheme}://{name}.{cfg.domain}"}


@app.post("/api/labs", status_code=status.HTTP_201_CREATED)
async def create_lab(data: LabCreate, admin: str = Depends(current_admin)):
    error = validate_name(data.name)
    if error:
        raise HTTPException(status_code=422, detail=error)
    display_name = data.display_name.strip() or data.name
    try:
        return await provisioner.create_lab(data.name, display_name)
    except ProvisionError as err:
        raise _provision_error(err) from err


@app.post("/api/labs/{name}/stop")
async def stop_lab(name: str, admin: str = Depends(current_admin)):
    try:
        return await provisioner.stop_lab(name)
    except ProvisionError as err:
        raise _provision_error(err) from err


@app.post("/api/labs/{name}/start")
async def start_lab(name: str, admin: str = Depends(current_admin)):
    try:
        return await provisioner.start_lab(name)
    except ProvisionError as err:
        raise _provision_error(err) from err


@app.post("/api/labs/{name}/reset-password")
async def reset_password(name: str, admin: str = Depends(current_admin)):
    try:
        return await provisioner.reset_password(name)
    except ProvisionError as err:
        raise _provision_error(err) from err


@app.delete("/api/labs/{name}")
async def delete_lab(name: str, admin: str = Depends(current_admin)):
    """Мягкое удаление: контейнер снимается, база остаётся до ручной очистки."""
    try:
        return await provisioner.delete_lab(name)
    except ProvisionError as err:
        raise _provision_error(err) from err


@app.post("/api/update-all")
async def update_all(admin: str = Depends(current_admin)):
    """docker pull свежего образа + пересоздание контейнеров активных лаб."""
    try:
        return await provisioner.update_all()
    except ProvisionError as err:
        raise _provision_error(err) from err


# ---------- Страница ----------

@app.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(BASE_DIR, "templates", "index.html"), encoding="utf-8") as fh:
        return HTMLResponse(fh.read())


@app.on_event("startup")
async def startup():
    await provisioner.init()
