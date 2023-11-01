docker system prune -a -f
docker rm $(docker ps -a -q) -f
docker rmi $(docker images -a -q) -f
sudo service docker restart
cd /root/laboratory_test_storage_service
git pull
docker-compose up