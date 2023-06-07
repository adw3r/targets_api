FROM python:3.11-alpine

COPY ./requirements/prod_requirements.txt .
RUN pip install -r prod_requirements.txt

COPY ./app ./app
COPY config.ini .

CMD uvicorn app.main:app --host=$HOST --port=$PORT
