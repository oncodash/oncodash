# Instructions to build and run the project with docker-compose

build and run the backend and frontend webservers and an nginx proxy server that passes requests to these servers.

## 1. Download Docker

- MacOS [Docker Desktop](https://docs.docker.com/desktop/mac/install/)
- Windows [Docker Desktop](https://docs.docker.com/desktop/windows/install/)
- Linux [Docker CE](https://docs.docker.com/engine/install/)

## 2. Download docker-compose
**If you installed Docker Desktop (MacOS/Windows) this is not needed**

- [Download docker-compose](https://docs.docker.com/compose/install/)
- [Running compose without sudo privliges](https://docs.docker.com/engine/install/linux-postinstall/)

## 3. Build the app

```sh
docker-compose build
```

## 4. Make migrations (Create SQL commands) and migrate (execute the SQL commands)

```sh
docker-compose run --rm backend sh -c "python manage.py makemigrations core"
docker-compose run --rm backend sh -c "python manage.py migrate"
```

## 3. Run the backend image in a container

```sh
docker-compose up
```

## 4. Develop

Open up the browser at `localhost` 
Browsable API at the `localhost/api/oncoviz/network/`

## 5. Run tests and linting for the backend

```sh
docker-compose run --rm backend sh -c "python manage.py test && flake8"
```

## 6. Run tests and linting for frontend

```sh
docker-compose run --rm nodeserver sh -c "npm test"
```