FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./app/requirements.txt ./
RUN pip install -U pip && \
    pip install -r requirements.txt
COPY ./app /app
RUN pytest /app/tests