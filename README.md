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

Grafana
```bash
docker run -d -p 3000:3000 --name=grafana -v grafana-storage:/var/lib/grafana grafana/grafana
```

### Compose

Running compose for local run:

```bash
docker-compose -f docker-compose.local.yml up
```

```yaml
# docker-compose.local.yml
version: "3"
services:
    arserver:
        image: alanjohn/argorithm-server:latest
        ports: 
            - 80:80
        volumes:
            - local-uploads:/app/app/uploads
volumes:
    local-uploads:
        driver: local
```

Running compose to emulation production setup:

```
docker-compose -f docker-compose.prod.yml up
```
```yml
# docker-compose.prod.yml
version: "3"
services:
	# database server
    mongodb:
        image: mongo
        ports: 
            - 27017:27017
        environment:
            - MONGO_INITDB_ROOT_USERNAME=${USERNAME}
            - MONGO_INITDB_ROOT_PASSWORD=${PASSWORD}
        volumes:
            - mongo-data:/data/db
    arserver:
        image: alanjohn/argorithm-server:latest
        ports: 
            - 80:80
        environment:
            - DATABASE=MONGO
            - AUTH=ENABLED
            - SECRET_KEY=${SECRET_KEY}
            - DB_USERNAME=${USERNAME}
            - DB_PASSWORD=${PASSWORD}
        volumes:
            - uploads:/app/app/uploads
        depends_on:
            - mongodb
volumes:
    mongo-data:
        driver: local
    uploads:
        driver: local
```

you'll need to setup a `.env` file for your environment variables or replace them in the `docker-compose.prod.yml`

```bash
AUTH=DISABLED
# AUTH : [ENABLED/DISABLED] activates authentication feature of server , needs database to be MONGO
DATABASE=MONGO
# DATABASE : [DISABLED/MONGO] activates db storage for data persistance
USERNAME=root
# USERNAME : Your database username
PASSWORD=example
# PASSWORD : your database password
SECRET_KEY=shh_its_secret
# SECRET_KEY : secret key for JWT token generation , required for AUTH
```

There are more env variables that can be setup 
refer `Dockerfile`