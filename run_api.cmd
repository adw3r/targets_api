docker build -t test_targets_api .
docker kill test_targets_api
docker run -d --rm -v C:\Users\Administrator\Desktop\targets_api:/myapp --env-file .env --name test_targets_api -p 8281:8281 test_targets_api
