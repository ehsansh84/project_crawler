FROM python:3.12.4-slim-bullseye

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

RUN apt update && apt install -y vim
RUN mkdir /app/logs
COPY . /app/
