FROM python:3.11-alpine

COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY ./app ./app

CMD uvicorn app.main:app --host=$HOST --port=$PORT
