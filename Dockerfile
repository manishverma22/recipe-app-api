FROM python:3.9-alpine3.13
LABEL maintainer="Manish Verma <manish.verma2@kellton.com>"

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
COPY requirements.dev.txt /app/requirements.dev.txt
COPY . /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r requirements.txt && \
    if [ "$DEV" = "true" ]; then \
        /py/bin/pip install -r requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/py/bin:$PATH"

USER django-user
