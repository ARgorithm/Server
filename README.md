# Server
Flask based REST API for ARgorithm
![Docker](https://github.com/ARgorithm/Server/workflows/Docker/badge.svg)

The application has an easy to use docker image so you should prefer installing docker before running it. The base image used to make application image is `tiangolo/uvicorn-gunicorn-fastapi:python3.8` which is docker image for running FastAPI applications in production utilizing uvicorn and gunicorn. 

Recommended you check out [ARgorithmToolkit](https://github.com/ARgorithm/Toolkit)

For testing , pytest has been used and all the tests can be found in `tests` folder

## Usage

you can go to `/docs` route to get the FastAPI Swagger UI to explore all the routes. You can also check out the documentation of ARgorithmToolkit at readthedocs for more details