<a href="https://oncodash.github.io/oncodash/"><img src="https://github.com/oncodash/oncodash/actions/workflows/build-docs.yml/badge.svg" alt="Build Status"/></a></td>

# Instructions to build and run the project with docker-compose

build and run the backend and frontend webservers and an nginx proxy server that passes requests to these servers.

## 1. Download Docker

- MacOS [Docker Desktop](https://docs.docker.com/desktop/mac/install/)
- Windows [Docker Desktop](https://docs.docker.com/desktop/windows/install/)
- Linux [Docker CE](https://docs.docker.com/engine/install/)

## 2. Download docker-compose
**If you installed Docker Desktop (MacOS/Windows) this is not needed**

- [Download docker-compose](https://docs.docker.com/compose/install/)
- [Running compose without sudo privileges](https://docs.docker.com/engine/install/linux-postinstall/)

## 3. Build the app

```sh
docker-compose build
```

## 4. Make migrations (Create SQL commands) and migrate (execute the SQL commands)

```sh
docker-compose run --rm backend sh -c "python manage.py makemigrations"
docker-compose run --rm backend sh -c "python manage.py migrate"
```

## 5. Run the oncodash image in a container

```sh
docker-compose up
```

## 6. Develop

- Open up the browser at `localhost` 
- Browsable API at `localhost/api/explainer/networks/`

## 7. Run tests and linting for the backend

```sh
docker-compose run --rm backend sh -c "python manage.py test && flake8"
```

## 8. Run tests and linting for the frontend

```sh
docker-compose run --rm nodeserver sh -c "npm test"
```
