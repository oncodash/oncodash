
To build and run Oncodash, you have two options:
- use *docker-compose* and run from a container (not working),
- run from your own local configuration.


# Build and run with docker-compose

Those instructions will build and run the backend and frontend webservers
from within containers, not touching anything on your operating system.

The composed container runs an nginx proxy server that passes requests to backend and
frontends containers.


## Requirements

- MacOS [Docker Desktop](https://docs.docker.com/desktop/mac/install/)
- Windows [Docker Desktop](https://docs.docker.com/desktop/windows/install/)
- Linux [Docker CE](https://docs.docker.com/engine/install/)
- [docker-compose](https://docs.docker.com/compose/install/) (not needed for MacOS/Windows)
- [Running compose without sudo privileges](https://docs.docker.com/engine/install/linux-postinstall/)


## Install Docker

### Ubuntu 20.04 LTS focal

```bash
# install dependencies
sudo apt install ca-certificates curl gnupg lsb-release checkinstall
# Download and install certificates
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
# Configure the package repository
echo   "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
# Install packages from the repository
sudo apt update && sudo apt install docker-ce docker-ce-cli containerd.io
# Download the docker-compose executable at version 2.0.1
sudo checkinstall curl -L  "https://github.com/docker/compose/releases/download/v2.0.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/docker-compose
# Make it executable
sudo chmod a+x /usr/local/bin/docker-compose
# Add at least the current user to the group able to execute docker
sudo usermod -aG docker ${USER}
```

You may need to restart your shell after installation.


### MacOS

Intel chip:
```bash
# Download the image
curl -L "https://desktop.docker.com/mac/main/amd64/Docker.dmg?utm_source=docker&utm_medium=webreferral&utm_campaign=docs-driven-download-mac-amd64" -o Docker.dmg
# Open the package
hdiutil attach Docker.dmg
# Install as an app
cp -a /Volumes/Docker/Docker.app /Applications/
```

You will be asked to accept some user contract at first launch.


## Installation

1. Let's Encrypt installation: 
    - go to https://certbot.eff.org/
    - select Software:Nginx System:Your-Host-OS
    - follow the instruction to install certbot and get certificates

1. Build the back-end, front-end and nginx docker-images:
    ```sh
    docker-compose build
    ```
1. Create a development SQLlite database inside the container and add tables to it:
    ```sh
    docker-compose run --rm backend sh -c "python manage.py makemigrations"
    docker-compose run --rm backend sh -c "python manage.py migrate"
    ```

1. Populate a test database with network data (Explainer-app)
    ```sh
    docker-compose run --rm backend sh -c "python manage.py flush --no-input"
    docker-compose run --rm backend sh -c "python manage.py populate -p /opt/app/path/to/indf.csv"
    ```
    Note: `/opt/app/` points by default to wherever is `oncodash/backend/` on your
    system.

1. Populate a test database with clinical data and real timeline data. "\<clinical filepath\>" is the path of clinical data file and can be downloaded from eduuni. "\<timeline filepath\>" is the timeline data file and can be downloaded from the eduuni repository (DECIDER/Clinical Data/timeline.csv). **The expected column separator is ";"**. The uploading takes several minutes, to shorten it you can reduce the timeline file by removing some lines.
    ```sh
    docker-compose run --rm backend sh -c "python manage.py import_timelinerecords_and_clinicaldata -clinicalpath <clinical filepath> -timelinepath <timeline  filepath>"
    ```

1. Create an account. Type:
    ```sh
    docker-compose run --rm backend sh -c "python manage.py createsuperuser"
    ```
    and then follow the prompt instruction.


## Development

1. Run the images in containers:
    If you are running containers for the first time:
    ```sh
    docker-compose up -d
    ```
1. Open up the browser at [localhost](http://localhost).
1. Browsable API endpoints at [localhost/api/explainer/networks/](http://localhost/api/explainer/networks/).


## Testing

```sh
docker-compose run --rm backend sh -c "python manage.py test && flake8"
```

```sh
docker-compose run --rm nodeserver sh -c "npm test"
```


# Build and run locally

## Requirements

- [nodejs](https://nodejs.org/en/download/)
- Python >= 3.7

## Installation

#### Let's Encrypt
    - go to https://certbot.eff.org/
    - select Software:Nginx System:Your-Host-OS
    - follow the instruction to install certbot and get certificates


#### Backend

1. Clone the repository & move to the `backend` directory:
```sh
git clone https://github.com/oncodash/oncodash.git
cd oncodash/backend/
```
2. Create a virtual environment.
You have two options: *Python's virtual environments* or *conda*:
```sh
python3 -m venv backendEnv
source backendEnv/bin/activate
pip install -U pip
```

***OR***

```sh
conda create --name backendEnv python=3.7
conda activate backendEnv
```

3. Install python dependencies:
```sh
pip install -r requirements.txt
```
4. Create a development SQLlite database and add tables to it:
```sh
python manage.py makemigrations
python manage.py migrate
```
5. Populate a test database with network data (Explainer-app)
```sh
python manage.py flush --no-input
python manage.py populate -p /path/to/indication_table.csv
```

6. Populate a test database with clinical data and real timeline data. "\<clinical filepath\>" is the path of clinical data file and can be downloaded from eduuni. "\<timeline filepath\>" is the timeline data file and can be downloaded from the eduuni repository (DECIDER/Clinical Data/timeline.csv). **The expected column separator is ";"**. The uploading takes several minutes, to shorten it you can reduce the timeline file by removing some lines.
```sh
python manage.py import_timelinerecords_and_clinicaldata -clinicalpath <clinical filepath> -timelinepath <timeline filepath>
```

7. Create an account. Type:
```sh
python manage.py createsuperuser
```
and then follow the prompt instruction.

8. Create CGI and OncoKB accounts to get corresponding tokens. Modify login email and tokens (OncoKB requires only token) in backend/backend/settings.py:
```
CGI_LOGIN = ""
CGI_TOKEN = ""
ONCOKB_TOKEN = ""
```
6. Import genomic variants to the data. "\<clinical filepath\>" is the path of clinical data file and can be downloaded from eduuni. "\<timeline filepath\>" is the timeline data file and can be downloaded from the eduuni repository (DECIDER/Clinical Data/timeline.csv). **The expected column separator is ";"**. The uploading takes several minutes, to shorten it you can reduce the timeline file by removing some lines.
```sh
python manage.py import_genomic_variants --copy_number_alterations \<cnv filepath\>"
```
#### Front-end

1. Move to the `oncodash-app` directory:
```sh
cd oncodash/oncodash-app/
```
2. Install node dependencies:
```
npm install --legacy-peer-deps
```

## Development

1. Run the back-end development server:
```sh
python manage.py runserver 0.0.0.0:8888
```
2. Run the front-end development server:
```
npm start
```
3. Open up the browser at [localhost:3000/](http://localhost:3000/) and login with the previously created backend credentials. Tested with Chrome.
4. Browsable API endpoints at [localhost:8888/api/explainer/networks/](http://localhost:8888/api/explainer/networks/).


## Testing

Backend:
```sh
python manage.py test && flake8
```

Frontend:
```sh
npm test
```

