
Ubuntu 20.04 LTS focal
======================

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

