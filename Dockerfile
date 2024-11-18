FROM python:3.8-slim

RUN apt-get update
RUN apt-get -y upgrade

WORKDIR  /usr/src/email
ENV PYTHONPATH /usr/src/email
ENV PYTHONHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV TZ America/Sao_Paulo

COPY ./ ./

ENTRYPOINT ["python", "app/main.py"]
