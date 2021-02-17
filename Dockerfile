FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

LABEL maintainer="Alan John <alansandra2013@gmail.com>"

# copy dependency requirements and install them
COPY ./app/requirements.txt ./
RUN update-ca-certificates && \
    pip install -U pip && \
    pip install -r requirements.txt

# add code file 
COPY ./app /app

# Required ENV variables to customise server application features
ENV SECRET_KEY=clawtime
ENV AUTH=DISABLED
ENV MAIL=DISABLED
ENV DATABASE=DISABLED
ENV CACHING=DISABLED

# Required for AUTH as intial administrator for server application
ENV ADMIN_EMAIL=sample@email.com
ENV ADMIN_PASSWORD=test123

# Database details for connecting to mongodb server
ENV DB_ENDPOINT=
ENV DB_PORT=27017
ENV DB_USERNAME=root
ENV DB_PASSWORD=example

# Redis server details for enabling caching
ENV REDIS_HOST=
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=

# If provided, secures /metrics path with bearer authorization
ENV METRICS_TOKEN=

RUN pytest /app/tests