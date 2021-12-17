# Instructions to build and run only the backend with docker-compose

## 1. Build the backend image

Navigate to the `../backend/` folder

```sh
docker-compose build
```

## 2. Make migrations (Create SQL commands) and migrate (execute the SQL commands)

```sh
docker-compose run --rm backend sh -c "python manage.py makemigrations"
docker-compose run --rm backend sh -c "python manage.py migrate"
```

## 3. Run the backend image in a container

```sh
$ docker-compose up
```

## 4. Develop

- Open up the browser at `localhost:8888` 
- Browsable API at `localhost:8888/api/explainer/network/`

## 5. Run tests and linting for backend

```sh
docker-compose run --rm backend sh -c "python manage.py test && flake8"
```
