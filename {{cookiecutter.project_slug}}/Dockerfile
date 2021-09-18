FROM python:{{cookiecutter.python_version}}-slim as builder
LABEL maintainer="{{cookiecutter.author}} <{{cookiecutter.email}}>"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends build-essential libffi-dev libxml2-dev \
    libxslt-dev curl libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

RUN python -m venv /venv
ENV PATH=/venv/bin:/root/.local/bin:${PATH}
RUN pip install --upgrade pip

WORKDIR /{{cookiecutter.project_slug}}
COPY pyproject.toml poetry.lock ./
RUN . /venv/bin/activate; \
    poetry install --no-dev

# ---------------------------------------------------------

FROM python:{{cookiecutter.python_version}}-slim as final

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev

COPY --from=builder /venv /venv
ENV PATH=/venv/bin:${PATH}

WORKDIR /{{cookiecutter.project_slug}}
USER nobody
COPY --chown=nobody:nogroup hypercorn.toml .
COPY --chown=nobody:nogroup app/ ./app

EXPOSE 5000

CMD ["hypercorn", "--config=hypercorn.toml", "app.main:app"]
