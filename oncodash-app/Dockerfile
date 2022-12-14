# FROM node:16-alpine as build

# # Add Tini. Checkout github
# # https://github.com/krallin/tini
# RUN apk add --no-cache tini
# ENTRYPOINT ["/sbin/tini", "--"]

# # Get latest npm
# RUN npm i npm@latest -g

# RUN echo $(whoami)

# # install dependencies first, in a different location for easier app
# # bind mounting for local development due to default /opt permissions
# # we have to create the dir with root and change perms
# RUN mkdir /opt/node_app && chown node:node /opt/node_app
# WORKDIR /opt/node_app

# COPY . .

# ENV PATH /opt/node_app/node_modules/.bin:$PATH

# RUN chown -R node:node /usr/local/lib/node_modules/
# RUN chmod -R 775 /usr/local/lib/node_modules/

# # the official node image provides an unprivileged user as a security
# # best practice but we have to manually enable it. We put it here so
# # npm installs dependencies as the same user who runs the app.
# # https://github.com/nodejs/docker-node/blob/master/docs/BestPractices.md#non-root-user
# USER node

# # copy package.json, install deps and set $PATH-var for node_modules
# COPY --chown=node:node package.json package-lock.json* ./

# RUN npm install --no-optional --legacy-peer-deps && npm cache clean --force
# # RUN npm ci
# RUN npm install react-scripts@latest
# RUN npm update chokidar --legacy-peer-deps

# # copy in our source code last, as it changes the most
# # copy in as node user, so permissions match what we need
# RUN mkdir /opt/node_app/app && chown node:node /opt/node_app/app
# WORKDIR /opt/node_app/app
# COPY . ./
# RUN npm run build

# COPY --chown=node:node . .

# # # app runs on port 8000
# EXPOSE 3000

# CMD ["npx", "serve", "build"]

# # start the dev server
# # CMD ["npm", "start"]
# # CMD ["npm", "start", "--prefix", "/opt/node_app/app"]

# # # # production environment
# # FROM nginx:stable-alpine
# # COPY --from=build /app/build /usr/share/nginx/html
# # # new
# # COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
# # EXPOSE 80
# # CMD ["nginx", "-g", "daemon off;"]

# ==== CONFIGURE =====
# Use a Node 16 base image
FROM node:16-alpine

# Set the working directory to /app inside the container
WORKDIR /opt/node_app

# Copy app files
COPY . .

# Install dependencies
# CMD ["npm", "install", "-g", "serve"]
RUN npm install -g npm@9.2.0
RUN npm install -g serve
RUN npm install --no-optional --legacy-peer-deps
# RUN npm install --no-optional --legacy-peer-deps && npm cache clean --force
# RUN npm ci
RUN npm install react-scripts@latest --force

# Build the app
RUN npm run build

# # Set the env to "production"
# ENV NODE_ENV production

# # Expose the port on which the app will be running (3000 is the default that `serve` uses)
# EXPOSE 3000

# # Start the app
CMD ["npm", "run", "build"]
CMD ["serve", "-s", "build"]