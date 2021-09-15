FROM node:16-alpine

# Add Tini. Checkout github
# https://github.com/krallin/tini
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]

# Get latest npm
RUN npm i npm@latest -g

# install packages
RUN mkdir /app && chown node:node /app
WORKDIR /app
USER node
COPY --chown=node:node ./package*.json ./
RUN npm install --no-optional && npm cache clean --force

# Copy in source code and build
COPY --chown=node:node . .

# app runs on port 8000
EXPOSE 8000

# start the server
CMD ["npm", "start"]