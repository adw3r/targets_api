FROM python:3.11-alpine

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./app ./app
COPY config.ini .

CMD uvicorn app.main:app --host=$HOST --port=$PORT
