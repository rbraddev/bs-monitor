FROM python:3.9.6-slim-bullseye

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl build-essential \
    && apt-get clean

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml poetry.lock ./
RUN poetry install --no-root

WORKDIR /usr/src

ENTRYPOINT [ "python", "start.py" ]