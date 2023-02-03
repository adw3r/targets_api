docker build -t targets_api .
docker kill targets_api
docker run -d --rm -v C:\Users\Administrator\Desktop\targets_api:/myapp --env-file .env --name targets_api -p 8181:8181 targets_api
