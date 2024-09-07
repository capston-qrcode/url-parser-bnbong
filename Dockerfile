LABEL authors="bnbong"
FROM python:3.12.1-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    chromium-driver \
    chromium-browser \

RUN pip install poetry

COPY pyproject.toml poetry.lock /app/

RUN poetry install --only main

COPY . /app/

CMD ["poetry", "run", "python", "main.py"]
