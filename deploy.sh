#!/usr/bin/env bash
# ============================================================
# Деплой LTS с ПОЛНОЙ чисткой Docker.
# Сносятся ВСЕ контейнеры и образы, демон перезапускается,
# всё собирается заново с нуля.
#
# ДАННЫЕ НЕПРИКОСНОВЕННЫ: ни одна команда ниже не трогает тома —
# нигде нет --volumes и -v. База (внешняя или в докере на
# именованном томе) и файлы S3 переживают деплой всегда.
# ============================================================
set -euo pipefail

cd /root/laboratory_test_storage_service

echo "== Останавливаем стек проекта (тома НЕ трогаем: без -v)"
docker-compose down --remove-orphans 2>/dev/null || true

echo "== Полная чистка: все контейнеры"
docker rm -f $(docker ps -a -q) 2>/dev/null || true

echo "== Полная чистка: все образы"
docker rmi -f $(docker images -a -q) 2>/dev/null || true

echo "== Прочий мусор (сети, кэш сборки; тома сохраняются — без --volumes)"
docker system prune -a -f

echo "== Перезапуск демона Docker"
sudo service docker restart
sleep 5

echo "== Обновление кода"
git pull

echo "== Сборка с нуля и запуск"
docker-compose up -d --build

echo "== Статус"
docker-compose ps

echo "== Health-check"
sleep 5
curl -fsS -o /dev/null -w "HTTP %{http_code}\n" http://localhost/ \
  || { echo "!! Приложение не отвечает — логи web:"; docker-compose logs --tail=50 web; exit 1; }

echo "== Готово"
