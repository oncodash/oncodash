# Oncodash Front-end

The Oncodash front-end serves the static content of the application and
interacts with the back-end API.

# Instructions to build the frontend locally for development

### Requirements
- [nodejs](https://nodejs.org/en/download/)
- typescript `npm install -g typescript`

## Installation
1. Clone the repository & move to `oncodash-app` dir
```sh
git clone https://github.com/oncodash/oncodash.git
cd oncodash/oncodash-app/
```

2.  Install packages
```
npm install
```

## Development
1. Run a development server
```
npm start
```

2. Run the typescript compiler in watch mode
```
tsc -w
```

3. Open up the browser at `http://localhost:8000/`

## Testing
```sh
npm test
```

# Instructions to build a frontend docker-image with docker-compose for development

### Requirements
- [Docker desktop/CE](https://docs.docker.com/engine/install/) 
- [Docker-compose](https://docs.docker.com/compose/install/)

## Installation
1. Clone the repository & move to `oncodash-app` dir
```sh
git clone https://github.com/oncodash/oncodash.git
cd oncodash/oncodash-app/
```

2. Build the frontend docker-image
```sh
docker-compose build
```

## Development
1. Run the frontend image in a container
```sh
docker-compose up
```

2. Develop
  
Open up the browser at `localhost:8000`

## Testing
```sh
docker-compose run --rm nodeserver sh -c "npm test"
```
