# Georeport backend

### Сервис для хранения результатов лабораторных испытаний грунтов. 

![Схема](https://github.com/MOSTDORGEOTREST/laboratory_test_storage_service/blob/master/diagram.png)

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

