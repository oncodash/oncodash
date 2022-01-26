# Oncodash Back-end

The oncodash back-end is used to serve API-endpoints for the front-end application

# Instructions to build the backend locally for development

### Requirements

- Python >= 3.7

## Installation

1. Clone the repository & move to `backend` dir

```sh
git clone https://github.com/oncodash/oncodash.git
cd oncodash/backend/
```

2. Create a virtual environment

```sh
python3 -m venv backendEnv
source backendEnv/bin/activate
pip install -U pip
```

or

```sh
conda create --name backendEnv python=3.7
conda activate backendEnv
```

3. Install dependencies

```sh
pip install -r requirements.txt
```

4. Create a development SQLlite database and add tables to it

```sh
python manage.py makemigrations
python manage.py migrate
```

5. Populate a test database with network data (Explainer-app)

```sh
python manage.py populate -p /path/to/indication_table.csv
```

## Development

1. Run a development server

```sh
python manage.py runserver 0.0.0.0:8888
```

2. Open up the browser at `localhost:8888/`
3. Browsable API endpoints at `localhost:8888/api/explainer/networks/`

## Testing and linting

```sh
python manage.py test && flake8
```

# Instructions to build a backend docker-image with docker-compose for development

### Requirements

- [Docker desktop/CE](https://docs.docker.com/engine/install/)
- [Docker-compose](https://docs.docker.com/compose/install/)

## Installation

1. Clone the repository & move to `backend` dir

```sh
git clone https://github.com/oncodash/oncodash.git
cd oncodash/backend/
```

2. Build the backend docker-image

```sh
docker-compose build
```

3. Create a development SQLlite database inside the container and add tables to it

```sh
docker-compose run --rm backend sh -c "python manage.py makemigrations"
docker-compose run --rm backend sh -c "python manage.py migrate"
```

4. Populate a test database with network data (Explainer-app)

```sh
docker-compose run --rm backend sh -c "python manage.py populate -p /opt/app/path/to/indf.csv"
```

## Development

1. Run the backend image in a container

```sh
$ docker-compose up
```

2. Open up the browser at `localhost:8888` and develop

## Testing

```sh
docker-compose run --rm backend sh -c "python manage.py test && flake8"
```
