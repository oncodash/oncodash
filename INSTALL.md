
# Dependencies

On your server, you need to install:
- [uv](https://docs.astral.sh/uv/)
- [npm](https://www.npmjs.com/)
    - Recommended way is through [nvm](https://github.com/nvm-sh/nvm)
- a working [Neo4j](https://neo4j.com/) server
    - Recommended way is through the Debian APT: https://debian.neo4j.com
- a working [OncodashKB](https://github.com/oncodash/oncodashkb) database on this Neo4j server.
- [tmux](https://github.com/tmux/tmux/wiki)

From the `frontend` directory, run `npm install`.
The backend will install its own dependencies at first start.


# Minimal Configuration

## Oncodash

Edit the file that configure the access to the Neo4j database: `backend_neo4j/oncodash_neo4j.toml`

It should look like:

```toml
[neo4j]
uri = "neo4j://localhost:7687"
user = "neo4j"
database = "oncodash"
```

# Run the server

From the root directory, run: `./start_oncodash.sh <backend IP> <frontend URL>`

The `<backend IP>` should be the IP on which your server is accessed.
The `<fronted URL>` should be the URL where the web browser will find the application.

If you are just testing Oncodash on a single machine, both parameters will use the same IP.
For instance: `./start_oncodash.sh 192.168.1.1 https://192.168.1.1`

This will start a tmux session with two panes, one for the backend server, another for the frontend one.


# Access the web application

Open the `<frontend URL>` in a Web brwoser.



# Optional configuration

## Environment variables

Optional environment variables may be set (see `start_oncodash.sh`) :

- `ONCODASH_API_URL`: the URL to the backend REST server,
- `ONCODASH_PUBLIC_PATH`: the root path ('/' by default),
- `ONCODASH_API_URL`: the URL to the AIforIA cloud image server.


## Access on an internet domain

Oncodash being a proof of concept, it does not implement access restriction.

If you plan to operate Oncodash on the internet, you will have to manage
all the security configuration by yourself:

- an SSL-capable web (HTTPS) server,
- serving a domain name,
- with a user-access control,
- and a reverse proxy.

If you don't understand any of those concept, we strongly suggest you
do not operate Oncodash as a web server, but ask a competent sysadmin
to do it for you.


### Reverse proxy config

The frontend server operates on port 3001.

The backend REST server operates on port 5000, and should be accessible
at least for the `/api` path.

Optionally, you may set up the `/ping` path for testing purposes.

