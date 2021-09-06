FROM node:16-alpine

# Add Tini. Checkout github
# https://github.com/krallin/tini
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]

# set our node environment, either development or production
# defaults to development, switch to prouction when needed
ARG NODE_ENV=development
ENV NODE_ENV $NODE_ENV

# default to port 3000 for node
ARG PORT=8000
ENV PORT $PORT

# Get latest npm
RUN npm i npm@latest -g

# install dependencies outside oncodash root for easier app bind mounting for local dev
# due to default /opt permissions we have to create the dir with root and change perms
RUN mkdir /opt/app/ && chown node:node /opt/app/
WORKDIR /opt/app

# Manually change to unprivilegded non-root user provided by the node official image
# and copy package.json files to the /opt/oncodash/, install packages and set PATH var
USER node
COPY --chown=node:node package.json package-lock.json* ./
RUN npm install --no-optional && npm cache clean --force
ENV PATH /opt/app/node_modules/.bin:$PATH

# Copy in the source code
RUN mkdir /opt/app/oncodash-app && chown node:node /opt/app/oncodash-app
WORKDIR /opt/app/oncodash-app
COPY --chown=node:node . .

# CMD ["npm", "start", "--prefix", "/opt/app/oncodash-app"]