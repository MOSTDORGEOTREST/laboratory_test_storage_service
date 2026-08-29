"""
Провижининг лабораторий: база в общем Postgres-кластере + контейнер web
из общего образа с метками Traefik.

Два режима:
- боевой: docker SDK + asyncpg (реестр лаб хранится в БД lts_admin);
- ADMIN_MOCK=1: без Docker и Postgres — реестр в JSON-файле, операции
  имитируются. Нужен для локальной разработки и e2e-тестов интерфейса.
"""

import asyncio
import json
import os
import re
import secrets
import string
from datetime import datetime, timezone

NAME_RE = re.compile(r"^[a-z][a-z0-9-]{1,19}$")
RESERVED_NAMES = {"admin", "www", "api", "traefik", "metrics", "postgres", "redis"}


class ProvisionError(Exception):
    """Ошибка провижининга с человекочитаемым сообщением."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gen_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class Config:
    def __init__(self):
        env = os.environ.get
        self.mock = bool(env("ADMIN_MOCK"))
        self.domain = env("DOMAIN", "lts.example.com")
        self.scheme = env("LAB_URL_SCHEME", "https")
        self.lts_image = env("LTS_IMAGE", "lts:latest")
        self.docker_network = env("DOCKER_NETWORK", "lts_default")
        self.pg_host = env("PG_HOST", "postgres")
        self.pg_port = env("PG_PORT", "5432")
        self.pg_admin_user = env("PG_ADMIN_USER", "postgres")
        self.pg_admin_password = env("PG_ADMIN_PASSWORD", "")
        self.redis_host = env("REDIS_HOST", "redis")
        self.redis_port = env("REDIS_PORT", "6379")
        self.redis_user = env("REDIS_USER", "default")
        self.redis_password = env("REDIS_PASSWORD", "")
        # S3 общий для всех лаб, у каждой — свой префикс ключей
        self.aws = {
            "AWS_URI": env("AWS_URI", ""),
            "AWS_ACCCESS_KEY": env("AWS_ACCCESS_KEY", ""),  # имя переменной как в основном приложении
            "AWS_SERVICE_NAME": env("AWS_SERVICE_NAME", "s3"),
            "AWS_SECRET_KEY": env("AWS_SECRET_KEY", ""),
            "AWS_REGION": env("AWS_REGION", ""),
            "AWS_BUCKET": env("AWS_BUCKET", ""),
        }
        self.mock_registry_path = env("ADMIN_MOCK_REGISTRY", "/tmp/lts_admin_labs.json")


def validate_name(name: str) -> str | None:
    """None — имя валидно, иначе текст ошибки."""
    if not NAME_RE.match(name or ""):
        return "Имя: 2–20 символов, латиница в нижнем регистре, цифры и дефис, начинается с буквы"
    if name in RESERVED_NAMES:
        return "Это имя зарезервировано"
    return None


def _lab_public(lab: dict) -> dict:
    """Публичное представление лабы — без секретов из config."""
    return {
        "name": lab["name"],
        "display_name": lab["display_name"],
        "url": lab["url"],
        "db_name": lab["db_name"],
        "s3_prefix": lab["s3_prefix"],
        "superuser_name": lab["config"]["SUPERUSER_NAME"],
        "status": lab["status"],
        "created_at": lab["created_at"],
    }


# ============================================================
# Мок-режим: реестр в JSON, операции имитируются
# ============================================================

class MockProvisioner:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._lock = asyncio.Lock()

    def _load(self) -> dict:
        try:
            with open(self.cfg.mock_registry_path) as fh:
                return json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save(self, labs: dict):
        with open(self.cfg.mock_registry_path, "w") as fh:
            json.dump(labs, fh, ensure_ascii=False, indent=1)

    async def init(self):
        pass

    async def list_labs(self):
        labs = sorted(self._load().values(), key=lambda l: l["created_at"])
        return [_lab_public(l) for l in labs]

    async def name_taken(self, name: str) -> bool:
        return name in self._load()

    async def create_lab(self, name: str, display_name: str) -> dict:
        async with self._lock:
            labs = self._load()
            if name in labs:
                raise ProvisionError("Лаборатория с таким именем уже существует")
            password = _gen_password()
            lab = {
                "name": name,
                "display_name": display_name,
                "url": f"{self.cfg.scheme}://{name}.{self.cfg.domain}",
                "db_name": f"lab_{name}".replace("-", "_"),
                "s3_prefix": f"{name}/",
                "config": {"SUPERUSER_NAME": f"admin_{name}", "SUPERUSER_PASSWORD": password},
                "status": "running",
                "created_at": _now(),
            }
            labs[name] = lab
            self._save(labs)
            return {"lab": _lab_public(lab),
                    "credentials": {"login": lab["config"]["SUPERUSER_NAME"], "password": password}}

    async def _set_status(self, name: str, status: str):
        async with self._lock:
            labs = self._load()
            if name not in labs:
                raise ProvisionError("Лаборатория не найдена")
            labs[name]["status"] = status
            self._save(labs)
            return _lab_public(labs[name])

    async def stop_lab(self, name):
        return await self._set_status(name, "stopped")

    async def start_lab(self, name):
        return await self._set_status(name, "running")

    async def delete_lab(self, name):
        return await self._set_status(name, "deleted")

    async def reset_password(self, name: str) -> dict:
        async with self._lock:
            labs = self._load()
            if name not in labs:
                raise ProvisionError("Лаборатория не найдена")
            password = _gen_password()
            labs[name]["config"]["SUPERUSER_PASSWORD"] = password
            self._save(labs)
            return {"login": labs[name]["config"]["SUPERUSER_NAME"], "password": password}

    async def update_all(self) -> dict:
        running = [l for l in self._load().values() if l["status"] == "running"]
        return {"updated": [l["name"] for l in running]}


# ============================================================
# Боевой режим: Postgres-реестр + Docker SDK
# ============================================================

class DockerProvisioner:
    def __init__(self, cfg: Config):
        import docker  # локальный импорт: в мок-режиме пакет не нужен
        import asyncpg  # noqa: F401
        self.cfg = cfg
        self.docker = docker.from_env()
        self._lock = asyncio.Lock()

    # ---------- Postgres ----------

    async def _admin_conn(self, database: str = "postgres"):
        import asyncpg
        return await asyncpg.connect(
            host=self.cfg.pg_host, port=int(self.cfg.pg_port),
            user=self.cfg.pg_admin_user, password=self.cfg.pg_admin_password,
            database=database,
        )

    async def init(self):
        """Создать служебную БД реестра lts_admin и таблицу labs."""
        conn = await self._admin_conn()
        try:
            exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = 'lts_admin'")
            if not exists:
                await conn.execute('CREATE DATABASE lts_admin')
        finally:
            await conn.close()
        reg = await self._admin_conn("lts_admin")
        try:
            await reg.execute("""
                CREATE TABLE IF NOT EXISTS labs (
                    name TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    db_name TEXT NOT NULL,
                    s3_prefix TEXT NOT NULL,
                    config JSONB NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
        finally:
            await reg.close()

    async def _registry(self):
        return await self._admin_conn("lts_admin")

    async def _get_lab(self, conn, name: str) -> dict:
        row = await conn.fetchrow("SELECT * FROM labs WHERE name = $1", name)
        if not row:
            raise ProvisionError("Лаборатория не найдена")
        lab = dict(row)
        lab["config"] = json.loads(lab["config"])
        return lab

    # ---------- Docker ----------

    def _container_name(self, name: str) -> str:
        return f"lts_web_{name}"

    def _lab_env(self, lab: dict) -> dict:
        cfg = lab["config"]
        return {
            # ЖЁСТКО prod: MODE=test делает drop_all и стирает базу лабы
            "MODE": "prod",
            "DATABASE_URL": cfg["DATABASE_URL"],
            "JWT_SECRET": cfg["JWT_SECRET"],
            "JWT_ALGORITHM": "HS256",
            "JWT_EXPIRATION": "30",
            "SUPERUSER_NAME": cfg["SUPERUSER_NAME"],
            "SUPERUSER_PASSWORD": cfg["SUPERUSER_PASSWORD"],
            "S3_PRE_KEY": lab["s3_prefix"],
            "REDIS_HOST": self.cfg.redis_host,
            "REDIS_PORT": self.cfg.redis_port,
            "REDIS_USER": self.cfg.redis_user,
            "REDIS_PASSWORD": self.cfg.redis_password,
            **self.cfg.aws,
        }

    def _run_container(self, lab: dict):
        name = lab["name"]
        cname = self._container_name(name)
        host = f"{name}.{self.cfg.domain}"
        self.docker.containers.run(
            self.cfg.lts_image,
            name=cname,
            detach=True,
            network=self.cfg.docker_network,
            restart_policy={"Name": "unless-stopped"},
            environment=self._lab_env(lab),
            labels={
                "lts.lab": name,
                "traefik.enable": "true",
                f"traefik.http.routers.{name}.rule": f"Host(`{host}`)",
                f"traefik.http.routers.{name}.entrypoints": "websecure",
                f"traefik.http.routers.{name}.tls.certresolver": "le",
                f"traefik.http.services.{name}.loadbalancer.server.port": "8000",
            },
        )

    def _get_container(self, name: str):
        import docker
        try:
            return self.docker.containers.get(self._container_name(name))
        except docker.errors.NotFound:
            return None

    def _container_status(self, name: str) -> str:
        c = self._get_container(name)
        return c.status if c else "absent"

    # ---------- Операции ----------

    async def list_labs(self):
        conn = await self._registry()
        try:
            rows = await conn.fetch("SELECT * FROM labs ORDER BY created_at")
        finally:
            await conn.close()
        result = []
        for row in rows:
            lab = dict(row)
            lab["config"] = json.loads(lab["config"])
            public = _lab_public(lab)
            if lab["status"] != "deleted":
                # живой статус — из Docker, а не из реестра
                docker_status = await asyncio.to_thread(self._container_status, lab["name"])
                public["status"] = {"running": "running", "exited": "stopped",
                                    "absent": "error"}.get(docker_status, docker_status)
            result.append(public)
        return result

    async def name_taken(self, name: str) -> bool:
        conn = await self._registry()
        try:
            return bool(await conn.fetchval("SELECT 1 FROM labs WHERE name = $1", name))
        finally:
            await conn.close()

    async def create_lab(self, name: str, display_name: str) -> dict:
        async with self._lock:
            if await self.name_taken(name):
                raise ProvisionError("Лаборатория с таким именем уже существует")
            if self._get_container(name) is not None:
                raise ProvisionError(f"Контейнер {self._container_name(name)} уже существует")

            db_name = f"lab_{name}".replace("-", "_")
            db_role = db_name
            db_password = _gen_password(24)
            superuser_password = _gen_password()
            lab = {
                "name": name,
                "display_name": display_name,
                "url": f"{self.cfg.scheme}://{name}.{self.cfg.domain}",
                "db_name": db_name,
                "s3_prefix": f"{name}/",
                "config": {
                    "SUPERUSER_NAME": f"admin_{name}",
                    "SUPERUSER_PASSWORD": superuser_password,
                    "JWT_SECRET": secrets.token_urlsafe(32),
                    "DATABASE_URL": (
                        f"postgresql+asyncpg://{db_role}:{db_password}"
                        f"@{self.cfg.pg_host}:{self.cfg.pg_port}/{db_name}"
                    ),
                },
                "status": "running",
                "created_at": _now(),
            }

            # 1. Роль и база (роль видит только свою базу)
            conn = await self._admin_conn()
            try:
                role_exists = await conn.fetchval("SELECT 1 FROM pg_roles WHERE rolname = $1", db_role)
                if role_exists:
                    raise ProvisionError(f"Роль {db_role} уже существует в кластере")
                # имена проверены регуляркой NAME_RE — интерполяция безопасна
                await conn.execute(f'CREATE ROLE "{db_role}" LOGIN PASSWORD \'{db_password}\'')
                await conn.execute(f'CREATE DATABASE "{db_name}" OWNER "{db_role}"')
            finally:
                await conn.close()

            # 2. Контейнер; при неудаче — откат базы и роли
            try:
                await asyncio.to_thread(self._run_container, lab)
            except Exception as err:
                conn = await self._admin_conn()
                try:
                    await conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
                    await conn.execute(f'DROP ROLE IF EXISTS "{db_role}"')
                finally:
                    await conn.close()
                raise ProvisionError(f"Не удалось запустить контейнер: {err}") from err

            # 3. Реестр
            reg = await self._registry()
            try:
                await reg.execute(
                    "INSERT INTO labs (name, display_name, url, db_name, s3_prefix, config, status, created_at) "
                    "VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
                    lab["name"], lab["display_name"], lab["url"], lab["db_name"],
                    lab["s3_prefix"], json.dumps(lab["config"]), lab["status"], lab["created_at"],
                )
            finally:
                await reg.close()

            return {"lab": _lab_public(lab),
                    "credentials": {"login": lab["config"]["SUPERUSER_NAME"],
                                    "password": superuser_password}}

    async def _set_status(self, name: str, status: str) -> dict:
        conn = await self._registry()
        try:
            lab = await self._get_lab(conn, name)
            await conn.execute("UPDATE labs SET status = $2 WHERE name = $1", name, status)
            lab["status"] = status
            return _lab_public(lab)
        finally:
            await conn.close()

    async def stop_lab(self, name: str) -> dict:
        c = self._get_container(name)
        if c:
            await asyncio.to_thread(c.stop)
        return await self._set_status(name, "stopped")

    async def start_lab(self, name: str) -> dict:
        c = self._get_container(name)
        if c is None:
            # контейнер пропал (например, после чистки docker) — пересоздаём из конфига
            conn = await self._registry()
            try:
                lab = await self._get_lab(conn, name)
            finally:
                await conn.close()
            await asyncio.to_thread(self._run_container, lab)
        else:
            await asyncio.to_thread(c.start)
        return await self._set_status(name, "running")

    async def delete_lab(self, name: str) -> dict:
        """Мягкое удаление: контейнер снимается, база остаётся (grace-период).

        Физическое удаление базы — вручную: DROP DATABASE lab_<name>;
        предварительно pg_dump, см. README.
        """
        c = self._get_container(name)
        if c:
            await asyncio.to_thread(c.stop)
            await asyncio.to_thread(c.remove)
        return await self._set_status(name, "deleted")

    async def reset_password(self, name: str) -> dict:
        async with self._lock:
            conn = await self._registry()
            try:
                lab = await self._get_lab(conn, name)
                password = _gen_password()
                lab["config"]["SUPERUSER_PASSWORD"] = password
                await conn.execute("UPDATE labs SET config = $2 WHERE name = $1",
                                   name, json.dumps(lab["config"]))
            finally:
                await conn.close()
            # применяем: пересоздаём контейнер с новым env
            c = self._get_container(name)
            if c:
                await asyncio.to_thread(c.stop)
                await asyncio.to_thread(c.remove)
            await asyncio.to_thread(self._run_container, lab)
            return {"login": lab["config"]["SUPERUSER_NAME"], "password": password}

    async def update_all(self) -> dict:
        """docker pull нового образа + пересоздание контейнеров активных лаб."""
        async with self._lock:
            await asyncio.to_thread(self.docker.images.pull, self.cfg.lts_image)
            conn = await self._registry()
            try:
                rows = await conn.fetch("SELECT * FROM labs WHERE status = 'running' ORDER BY name")
            finally:
                await conn.close()
            updated = []
            for row in rows:
                lab = dict(row)
                lab["config"] = json.loads(lab["config"])
                c = self._get_container(lab["name"])
                if c:
                    await asyncio.to_thread(c.stop)
                    await asyncio.to_thread(c.remove)
                await asyncio.to_thread(self._run_container, lab)
                updated.append(lab["name"])
            return {"updated": updated}


def make_provisioner(cfg: Config):
    return MockProvisioner(cfg) if cfg.mock else DockerProvisioner(cfg)
