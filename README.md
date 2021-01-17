# Server
Flask based REST API for ARgorithm
![Docker](https://github.com/ARgorithm/Server/workflows/Docker/badge.svg)

The application has an easy to use docker image so you should prefer installing docker before running it. The base image used to make application image is `tiangolo/uvicorn-gunicorn-fastapi:python3.8` which is docker image for running FastAPI applications in production utilizing uvicorn and gunicorn. 

Recommended you check out [ARgorithmToolkit](https://github.com/ARgorithm/Toolkit)

For testing , pytest has been used and all the tests can be found in `tests` folder

## Setup

You can clone the server and run

```bash
$ git clone https://github.com/ARgorithm/Server.git
$ cd Server/app/
$ pip install -r requirements.txt
$ uvicorn app.main:app
```

### Docker setup

You can pull the docker image from dockerhub

```bash
$ docker pull alanjohn/argorithm-server:latest
```

.... or you can build it yourself

```
$ docker build . -t argorithm-server:latest
```

The application can be run in different modes

1. In-app database

   No authentication or authorization services. Data stored using sqlite database. By default, it runs in this mode

2. mongodb database

   No authentication or authorization services. Data stored in mongodb database of your choice. For this you will need to set some environment variables:

   - DATABASE=mongodb
   - DB_USERNAME=yourdbusername
   - DB_PASSWORD=yourdbpassword
   - DB_ENDPOINT=yourdbendpoint
   - DB_PORT=27017

3. mongodb with auth

   Authorization on all basic routes. Data stored in mongodb database of your choice. This is an enhancement to the previous mode so along with the required envs previously

   - SECRET_KEY=yoursecretkey
   - ADMIN_EMAIL=sample@email.com
   - ADMIN_PASSWORD=test123

The repo comes with two docker compose configuration files

- `docker-compose.local.yml` : runs application in default mode
- `docker-compose.prod.yml` : runs application with mongodb and auth and will setup mongodb database as well. will read env variables from `.env` file [NOT PROVIDED].

## Usage

you can go to `/docs` route to get the FastAPI Swagger UI to explore all the routes. You can also check out the documentation of ARgorithmToolkit at readthedocs for more details