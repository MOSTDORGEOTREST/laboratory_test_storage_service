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

## Деплой:
~/ = папка проекта 

1. Скопировать файл .env в ~/
 
2. Открыть папку ~/ в терминале и выполнить:\
    `git init`\
    `git clone https://github.com/MOSTDORGEOTREST/laboratory_test_storage_service.git`

3. Запуск через docker-compose:\
    `docker-compose up --force-recreate -d --build`


Для очищения докера от проекта:\
    `docker rm $(docker ps -a -q) -f`\
    `docker rmi $(docker images -a -q) -f`

