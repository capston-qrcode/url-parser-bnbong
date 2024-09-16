FROM python:3.12.1-bookworm
MAINTAINER bnbong "bbbong9@gmail.com"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    chromium-driver \
    chromium

RUN pip install poetry webdriver-manager

COPY pyproject.toml poetry.lock /app/

RUN poetry install --only main

COPY . /app/

CMD ["poetry", "run", "python", "main.py"]
