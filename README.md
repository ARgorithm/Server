# Server
Flask based REST API for ARgorithm
![Docker](https://github.com/ARgorithm/Server/workflows/Docker/badge.svg)

The application is run using docker so you should prefer installing docker before running it. The base image used to make application image is `tiangolo/uwsgi-nginx-flask:python3.8` which is docker image for running flask apps in production utilizing nginx and uwsgi. You can check out at Sebastian Ramirez's [github repo](https://github.com/tiangolo/uwsgi-nginx-flask-docker) for the image 

Recommended you check out [ARgorithmToolkit](https://github.com/ARgorithm/Toolkit)

For testing , pytest has been used and all the tests can be found in `tests` folder

### Usage

Pulling the image:

```bash
docker pull alanjohn/argorithm/server
```
```bash
docker run --rm --name arserver -p 80:80 alanjohn/argorithm-server:latest
```

Building the image :

```bash
docker build -t argorithm-server .
```
```bash
docker run --rm --name arserver -p 80:80 argorithm-server
```

