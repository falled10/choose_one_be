FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/src/app

RUN pip install poetry

WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml /usr/src/app/

RUN poetry install

ADD . /usr/src/app

ENTRYPOINT ["./entrypoint.sh"]