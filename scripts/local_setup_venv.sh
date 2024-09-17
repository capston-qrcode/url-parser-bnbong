python -m venv venv

# Linux / MacOS
source venv/bin/activate

pip install poetry

poetry install --only main
