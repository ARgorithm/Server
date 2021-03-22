FROM python:3.8-slim

LABEL maintainer="Alan John <alansandra2013@gmail.com>"

# copy dependency requirements and install them
COPY ./app/requirements.txt ./
RUN update-ca-certificates && \
    pip install -U pip && \
    pip install -r requirements.txt

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./app /app
WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 80

RUN pytest tests

CMD ["/start.sh"]