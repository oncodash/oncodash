FROM node:20-alpine AS builder

WORKDIR /usr/opt/app

# Copy only the relevant files to build the application
COPY ./src/ ./src/
COPY ./package.json ./package.json
COPY ./package-lock.json ./package-lock.json
COPY ./tsconfig.json ./tsconfig.json
COPY ./vite.config.ts ./vite.config.ts

# Allow to setup this env variable for the docker build
ARG ONCODASH_API_URL

# Install all dependencies
RUN npm ci

# Switch to production mode for the build
ENV NODE_ENV="production"
RUN npm run build

# Document the port
EXPOSE 3001

# Setup the command to run the container
CMD [ "npm", "start" ]
