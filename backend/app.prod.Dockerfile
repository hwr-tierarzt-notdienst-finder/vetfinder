FROM python:3.10-bullseye AS setup_python_venv

COPY ./backend/requirements.txt /requirements.txt

RUN pip install -r requirements.txt


FROM setup_python_venv AS run

COPY ./shared-bash.sh /app/shared-bash.sh
COPY ./backend/ /app/backend/

# Will not be discovered as project root unless .git directory exists
RUN mkdir /app/.git

WORKDIR /app/backend/

VOLUME logs

# Start API
ENTRYPOINT ENV=prod PYTHONPATH=./src ./src/entrypoints/api.sh
