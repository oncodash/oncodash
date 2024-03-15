FROM node:20-alpine AS builder

WORKDIR /usr/opt/app

# Copy only the relevant files to build the application
COPY ./src/ ./src/
COPY ./package.json ./package.json
COPY ./package-lock.json ./package-lock.json
COPY ./tsconfig.json ./tsconfig.json
COPY ./vite.config.ts ./vite.config.ts

# Setup env variables for build
ARG ONCODASH_API_URL
ARG ONCODASH_PUBLIC_PATH

# Install all dependencies
RUN npm ci

# Setup env variables for build
ENV ONCODASH_API_URL = ${ONCODASH_API_URL}
ENV ONCODASH_PUBLIC_PATH = ${ONCODASH_PUBLIC_PATH}
ENV NODE_ENV="production"
RUN npm run build

# Document the port
EXPOSE 3001

# Setup the command to run the container
CMD [ "npm", "start" ]
