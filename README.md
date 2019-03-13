- [pydocker](#pydocker)
- [Setup](#Setup)
  - [Docker setup](#Docker-setup)
  - [Build Example Image](#Build-Example-Image)
  - [Install pydocker](#Install-pydocker)
  - [Setup pydocker](#Setup-pydocker)
- [Using pydocker](#Using-pydocker)
  - [Start ssh-agent container](#Start-ssh-agent-container)
  - [Launch](#Launch)
    - [Google Cloud Setup (optional)](#Google-Cloud-Setup-optional)
  - [Development](#Development)
    - [Setup](#Setup-1)
    - [Tests](#Tests)
    - [Continuous Integrations](#Continuous-Integrations)
    - [Versions and Tags](#Versions-and-Tags)
  - [License](#License)


# pydocker
This goal of **pydocker** is to make it seamless to work on a docker container on your laptop like you would with your normal environment. This means it handles passing all of your credentials (SSH key, Google, etc) and mounting a directory of your choosing from the host machine to the container, and sets up port forwarding so that you can still use notebooks. It supports local images, Google Container Repository, or anywhere docker can pull from.

# Setup

**(Note: These instructions currently only support MacBooks but pydocker should work on other OS.)**

Before you install the library there are some minimal environment setup steps.



## Docker setup

Install and start Docker:

```
brew cask install docker
open /Applications/Docker.app
```

## Build Example Image
**Dockerfile**
```dockerfile
FROM google/cloud-sdk:slim
RUN pip install jupyterlab notebook pandas
RUN  /bin/echo -e '#!/bin/bash\njupyter notebook --notebook-dir="/" --ip=0.0.0.0 --allow-root --NotebookApp.token=""' > /usr/bin/notebook && \
    chmod +x /usr/bin/notebook && \
     /bin/echo -e '#!/bin/bash\njupyter lab --notebook-dir="/" --ip=0.0.0.0 --allow-root --NotebookApp.token=""' > /usr/bin/lab && \
    chmod +x /usr/bin/lab
WORKDIR /current
CMD notebook
```
This Dockerfile uses the current directory as the workspace, and will look for all files there and the build command, `docker build -t notebook -f Dockerfile .`, will create a local docker image called **Notebook**, which uses the *google/cloud-sdk* as a base image. The Dockerfile also then makes a couple of small scripts to make it easier to launch notebooks or jupyterlab.


## Install pydocker

```
pip install sq-pydocker
```


## Setup pydocker
Make the directory
```
pydocker init
```
This will copy your ssh keys, and create a new config based on your main square config, but modified because of running in a docker container. This only needs to be run the first time.


# Using pydocker
```
Usage: pydocker [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose
  --help         Show this message and exit.

Commands:
  agent
  init
  launch
```



## Start ssh-agent container
If you need to have the ability to ssh into machines you can start an ssh-agent in a container with:
```python
pydocker agent
```
This will add keys copied with the `init` command without passwords automatically, or print the command you need to run to add password protected keys. This `ssh-agent` container will then be connected to all other containers, so you don't need to keep entering your key password. The makes it more secure by not storing any credentials in the Image. This container can be restarted when needed, if you run `pydocker agent` it will delete the container, and make a new one.


## Launch
```
Options:
  -i, --image TEXT        Docker image
  -n, --name TEXT         container name
  -d, --working_dir TEXT  host directory to mount
  -p, --port INTEGER      local port to be connected to container
  -l, --logs              stream container logs
  --gcloud / --no-gcloud  include gcloud credentials
  -c, --command TEXT      command which is passed to container
  --help                  show this message and exit.
```

This command launches the notebook (which we built above) and forwards internal port 8888 to the laptops port 9000 and creates a container named test.  In addition the host's current folder `.` is mounted in the **working_dir** folder. This gives the container access to the host filesystem. After running the command you can go to `localhost:9000` in your browser.

```
pydocker launch --image notebook --name test --working_dir . --port 9000 --no-gcloud
```

Remote images also work:
```
pydocker launch --image jupyter/minimal-notebook:latest --name example --working_dir . --port 9000 --no-gcloud
```
Will pull the remote image down first. You can still do `docker pull IMAGE` and pydocker will use the already downloaded image.

### Google Cloud Setup (optional)
This is only required if you are going to be using Google Cloud. If you already have gcloud installed, update by running `gcloud components update`. If you have not setup Google Cloud already, begin by installing Google Cloud.

  1. Download the (archive)(https://cloud.google.com/sdk/docs/quickstart-mac-os-x) and unpack it (only do the "Before you begin" section).

  2. Navigate to the folder containing `google-cloud-sdk` and run
```bash
./google-cloud-sdk/install.sh
```

  3. Set your gcloud account and project.
```bash
gcloud auth login
gcloud config set account ${USER}@squareup.com
gcloud config set project YOUR_PROJECT
gcloud auth application-default login
```

  4. Now generate your ssh credentials by running:
```bash
gcloud compute ssh --zone "us-central1-a" "RUNNING_VM"
```

## Development

### Setup

`pip install -e .`

### Tests

* `pytest` runs the unit tests
* `flake8` to check style guidelines

To run them locally:

    flake8 .
    pytest

### Continuous Integrations
CI is handled through travis, and will run non-GCS tests on both 2.7 and 3.6.
We may add cloud storage tests to travis soon, but for now tests should also be
run locally to confirm that functionality works as well.


### Versions and Tags
Use bumpversion to update the version of the package

    bumpversion [major|minor|patch]

This will increment the version and update it both in `setup.py` and `pydocker/__init__.py`.
It will also automatically commit a tag with the corresponding version. You can push this to the repo
with

    git push --tags


## License

Copyright 2018 Square, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.