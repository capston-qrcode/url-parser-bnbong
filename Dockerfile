FROM python:3.12.1-bookworm
MAINTAINER bnbong "bbbong9@gmail.com"

WORKDIR /app

# for ARM64 chromium installation
RUN apt-get update -y

RUN apt-get install software-properties-common -y

# RUN add-apt-repository ppa:xtradeb/apps -y

RUN apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    chromium \
    chromium-driver 

RUN pip install poetry

COPY pyproject.toml poetry.lock /app/

RUN poetry install --only main

COPY . /app/

CMD ["poetry", "run", "python", "main.py"]
