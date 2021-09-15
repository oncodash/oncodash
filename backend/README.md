# Instructions to build only the backend
## 1. Download Docker
    - Download link

## 2. Download docker-compose
    - Download link
    - Running compose without sudo privliges

## 3. Build the backend

Navigate to the `/backend/` folder

```
docker-compose build
```

## 4. Make migrations and migrate database
```
docker-compose run --rm oncodash sh -c "python manage.py migrate"
```

## 5. Run the backend container
```
docker-compose up
```

## 6. Develop
Open up the browser at `localhost:8888`
Browsable API at the `localhost:8888/api/oncoviz/network/`

## 7. Run tests and linting
```
docker-compose run --rm oncodash sh -c "python manage.py test && flake8"
```

