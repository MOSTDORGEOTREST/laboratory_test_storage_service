# MDGT Laboratory Test Storage Service

### Сервис для хранения результатов лабораторных испытаний грунтов. 

![Схема](https://github.com/MOSTDORGEOTREST/laboratory_test_storage_service/blob/main/diagram.png)

#### Функционал:
* авторизация по токену (JWT)
* сервис для доступа к бд результотов опытов (postgres)
* сервис для доступа к бд файлов опытов (S3)

#### Стек:
* fastapi
* postgresql
* sqlalchemy
* s3
* redis
* pytest

#### [Схема БД](https://dbdiagram.io/d/tests-64ba6ebc02bd1c4a5e791c6c)

## Переменные окружения для запуска:
    SUPERUSER_NAME=...
    SUPERUSER_PASSWORD=...
    POSTGRES_USER=...
    POSTGRES_PASSWORD=...
    POSTGRES_PORT=...
    POSTGRES_HOST=...
    POSTGRES_NAME=...
    JWT_SECRET=...
    JWT_ALGORITHM=...
    JWT_EXPIRATION=...
    AWS_URI=...
    AWS_ACCCESS_KEY=...
    AWS_SERVICE_NAME=...
    AWS_SECRET_KEY=...
    AWS_REGION=...
    AWS_BUCKET=...
    REDIS_PORT=...
    S3_PRE_KEY=...
    REDIS_HOST=...
    REDIS_PORT=...
    REDIS_USER=...
    REDIS_PASSWORD=...

## Деплой:
 
1. Открыть папку /root/ в терминале и выполнить:\
    `git init`\
    `git clone https://github.com/MOSTDORGEOTREST/laboratory_test_storage_service.git`

2. Скопировать файл .env в /root/laboratory_test_storage_service

3. Запуск ПРОД (web + nginx; Postgres/Redis/S3 — внешние, из .env):\
    `docker-compose up`

   Локальный дев-стек (свои Postgres и Redis; база НЕ очищается):\
    `docker-compose -f docker-compose-dev.yml up`

4. Запуск тестов — ТОЛЬКО через тестовый стек (он единственный чистит базу,
   для этого нужны сразу два флага: MODE=test и ALLOW_DB_DROP=1):\
    `docker-compose -f docker-compose.test.yml up -d`\
    `docker-compose -f docker-compose.test.yml exec web pytest . -v`

> Безопасность данных: приложение никогда не удаляет таблицы само по себе —
> на старте выполняется только create_all (создание недостающих).
> Очистка БД требует ОДНОВРЕМЕННО MODE=test и ALLOW_DB_DROP=1;
> ни прод-, ни дев-compose эти флаги не передают.


Для очищения докера от проекта:\
    `docker rm $(docker ps -a -q) -f`\
    `docker rmi $(docker images -a -q) -f`

