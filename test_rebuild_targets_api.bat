docker-compose build test-targets-api
docker-compose kill test-targets-api
docker-compose up -d --scale test-targets-api