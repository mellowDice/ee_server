docker pull erinkav/ee-server
docker stop socket_service
docker rm socket_service
docker run --name test_socket_service -d -p 80:9000 -e APP_CONFIG_FILE='config/production.py'  erinkav/test_ee_server