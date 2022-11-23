FROM python:3.10-bullseye AS setup_python_venv

COPY ./shared_python/requirements.txt /shared_requirements.txt
COPY ./backend/requirements.txt /requirements.txt

RUN pip install -r shared_requirements.txt -r requirements.txt


FROM setup_python_venv AS run

COPY ./shared-bash.sh /app/shared-bash.sh
COPY ./shared_python/ /app/shared_python/
COPY ./backend/ /app/backend/

# Will not be discovered as project root unless .git directory exists
RUN mkdir /app/.git

WORKDIR /app/backend/

VOLUME logs

# Start app
ENTRYPOINT ENV=prod PYTHONPATH=./src python ./src/entrypoints/setup_secrets.py \
    && rm secrets/token_hashes.json \
    && ENV=prod PYTHONPATH=./src ./src/entrypoints/app.sh
