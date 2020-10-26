FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./app/requirements.txt ./
RUN pip install -U pip && \
    pip install -r requirements.txt
COPY ./app /app

ENV AUTH=DISABLED
ENV DATABASE=DISABLED
ENV USERNAME=root
ENV PASSWORD=example

RUN pytest /app/tests