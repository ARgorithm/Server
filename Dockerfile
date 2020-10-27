FROM tiangolo/uwsgi-nginx-flask:python3.8

LABEL maintainer="Alan John <alansandra2013@gmail.com>"

COPY ./app/requirements.txt ./
RUN pip install -U pip && \
    pip install -r requirements.txt
COPY ./app /app

ENV AUTH=DISABLED
ENV MAIL=DISABLED
ENV DATABASE=DISABLED
ENV DB_USERNAME=root
ENV DB_PASSWORD=example
ENV ADMIN_EMAIL=sample@email.com
ENV ADMIN_PASSWORD=test123

RUN pytest /app/tests