<a  href="https://oncodash.github.io/oncodash/"><img  src="https://github.com/oncodash/oncodash/actions/workflows/build-docs.yml/badge.svg"  alt="Build Status"/></a></td>

# Oncodash

# Instructions to build and run the project with docker-compose for development

build and run the backend and frontend webservers and an nginx proxy server that passes requests to these servers.

## Requirements

- MacOS [Docker Desktop](https://docs.docker.com/desktop/mac/install/)
- Windows [Docker Desktop](https://docs.docker.com/desktop/windows/install/)
- Linux [Docker CE](https://docs.docker.com/engine/install/)
- [docker-compose](https://docs.docker.com/compose/install/) (not needed for MacOS/Windows)
- [Running compose without sudo privileges](https://docs.docker.com/engine/install/linux-postinstall/)

## Installation

1. Build the back-end, front-end and nginx docker-images

```sh
docker-compose build
```

2. Create a development SQLlite database inside the container and add tables to it

```sh
docker-compose run --rm backend sh -c "python manage.py makemigrations"
docker-compose run --rm backend sh -c "python manage.py migrate"
```

3. Populate a test database with network data (Explainer-app)

```sh
docker-compose run --rm backend sh -c "python manage.py populate -p /opt/app/path/to/indf.csv"
```

## Development

1. Run the images in containers

```sh
docker-compose up
```

2. Open up the browser at `localhost`
3. Browsable API endpoints at `localhost/api/explainer/networks/`

## Testing

```sh
docker-compose run --rm backend sh -c "python manage.py test && flake8"
```

```sh
docker-compose run --rm nodeserver sh -c "npm test"
```

# Instructions to build the project locally for development

## Requirements

- [nodejs](https://nodejs.org/en/download/)
- typescript `npm install -g typescript`
- Python >= 3.7

## Installation

#### Back-end

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

3. Install python dependencies

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

#### Front-end

1. move to `oncodash-app` dir

```sh
cd oncodash/oncodash-app/
```

2. Install node dependencies

```
npm install
```

## Development

1. Run the back-end development server

```sh
python manage.py runserver 0.0.0.0:8888
```

2. Run the front-end development server

```
npm start
```

3. Open up the browser at `http://localhost:8000/`
4. Browsable API endpoints at `localhost:8888/api/explainer/networks/`

## Testing

```sh
python manage.py test && flake8
```

```sh
npm test
```
