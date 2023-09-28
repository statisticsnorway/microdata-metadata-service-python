# Export Poetry Packages
FROM ubuntu:22.04 as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install python 3.9
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    python3.9 \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.9 /usr/bin/python

# Install tools
RUN apt-get update \
    && apt-get install -y  --no-install-recommends \
    ca-certificates \
    curl \
    build-essential \
    python3-distutils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Install poetry and export dep endencies to requirements yaml
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION
RUN poetry export > requirements.txt

# Production image
FROM python:3.9-slim-bullseye

# Create user
RUN groupadd --gid 180291 microdata \
    && useradd --uid 180291 --gid microdata --shell /bin/bash --create-home microdata 

WORKDIR /app
COPY metadata_service metadata_service
COPY --from=builder /app/pyproject.toml pyproject.toml
COPY --from=builder /app/requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#the output is sent straight to terminal without being first buffered
ENV PYTHONUNBUFFERED 1

# Change to our non-root user
USER microdata

CMD ["gunicorn", "metadata_service.app:app", "--workers", "1"]
