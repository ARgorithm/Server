FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

LABEL maintainer="Alan John <alansandra2013@gmail.com>"

COPY ./app/requirements.txt ./
RUN update-ca-certificates && \
    pip install -U pip && \
    pip install -r requirements.txt
COPY ./app /app

ENV SECRET_KEY=clawtime
ENV AUTH=DISABLED
ENV MAIL=DISABLED
ENV DATABASE=DISABLED
ENV DB_ENDPOINT=
ENV DB_PORT=27017
ENV DB_USERNAME=root
ENV DB_PASSWORD=example
ENV ADMIN_EMAIL=sample@email.com
ENV ADMIN_PASSWORD=test123

ENV CACHING=DISABLED
ENV REDIS_HOST=
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=

RUN pytest /app/tests