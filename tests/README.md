# Mender Integration Testing

![Mender logo](../mender_logo.png)

**Table of Contents**

- [Mender Integration Testing](#mender-integration-testing)
    - [Getting Started](#getting-started)
    - [Installing Dependencies](#installing-dependencies)
        - [Isolating Python Dependencies (Optional, but recommended)](#isolating-python-dependencies-optional-but-recommended)
            - [Install](#install)
            - [Initialize the Virtual Environment](#initialize-the-virtual-environment)
                - [(Optional) -- Select Python Version](#optional----select-python-version)
            - [Activate the Virtual Environment](#activate-the-virtual-environment)
        - [Local Dependencies](#local-dependencies)
        - [Debian](#debian)
        - [Alpine Linux](#alpine-linux)
        - [Python2 and Python3](#python2-and-python3)
    - [Running the Tests Locally](#running-the-tests-locally)
        - [Running the Tests](#running-the-tests)
    - [Modifying the Docker Images Employed](#modifying-the-docker-images-employed)
        - [Example -- Running with a Custom Backend Service](#example----running-with-a-custom-backend-service)
        - [Example -- Running with a Custom Client](#example----running-with-a-custom-client)
    - [Known Issues](#known-issues)
        - [SSH](#ssh)
        - [OS X](#os-x)
    - [Tips and Tricks](#tips-and-tricks)


-------------------------------------------------------------------------------


## Getting Started

The dependencies for the integration tests are collected and organized in
dependency files in the `./requirements` folder, and separated into


| Debian                 | Alpine                 | Python                    |
| :-------------:        | :-------------:        | :-----:                   |
| *deb-requirements.txt* | *apt-requirements.txt* | *python-requirements.txt* |

## Installing Dependencies

### Isolating Python Dependencies (Optional, but recommended)

In order to avoid dependency mismanagement due to Python packages differing from
one test environment to the other, it is recommended to use a python virtual
environment. The "de-facto" standard is
[virtualenv](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

#### Install

```bash
$ pip install virtualenv
```

> Make sure that you are using the correct version of pip (In this case, pip2).

#### Initialize the Virtual Environment

```bash
$ cd <integration-dir>/tests
$ virtualenv <name-of-virtualenv-folder>
```

##### (Optional) -- Select Python Version
```bash
$ virtualenv -p /usr/bin/python2.7 <name-of-virtualenv-folder>
```

#### Activate the Virtual Environment

```bash
$ source <name-of-virtualenv-folder>/bin/activate
```

This now means that you have a clean Python environment, and no packages you
have previously installed outside of this virtual environment will be
discoverable by Python.

Verify the virtual-environment through running

```bash
$ python2 --version
  python 2.7.x
$ which python2
  /path/to/current/dir/venv/bin/python
```

Once you are done, the virtual environment is deactivated with

```bash
$ deactivate
```

### Local Dependencies

### Debian

```bash
$ apt install -yyq $(cat requirements/deb-requirements.txt)
```

### Alpine Linux

```bash
$ apk --update add $(cat requirements/apk-requirements.txt)
```

### Python2 and Python3

```bash
$ pip2  install  -r requirements/python-requirements.txt
$ pip3  install  -r requirements/python-requirements.txt
```

> The Python install works the same whether or not a Python virtual-environment
> is active. But with a virtual-environment active, the dependencies will keep
> your native Python environment clean. Also remember that the virtual
> environment is only enabled for Python2 with this setup.


-------------------------------------------------------------------------------


## Running the Tests Locally

> The tests can be run locally without any further involvement as long as all
> the dependencies have been installed and are at the correct version. However,
> managing dependencies, especially with Python can be a hassle. Therefore it is
> recommended to add a virtual Python environment to isolate the dependencies
> needed for running the integration tests.

### Running the Tests

Next, run all the tests (Open-Source and Enterprise) with the `run.sh` script.

```bash
$ ./run.sh
```

Run only the Open-Source tests with

```bash
$ ./run.sh -- -k 'not Enterprise'
```

And Enterprise only

```bash
$  ./run.sh -- -k 'Enterprise'
```

**NOTE**: This is dependent upon having a functioning Docker environment, and being
logged in to `registry.mender.io`.

## Modifying the Docker Images Employed

In order to run the integration tests with the local changes made to some Mender
service, it is necessary to build the container, and tag it with the matching
tag employed in the integration repository. This can be found in the
`docker-compose.yml` file in the root directory, under the `image:` key.

#### Example -- Running with a Custom Backend Service

For the backend services there exists a `Dockerfile` in the root repository, and
as such a new image can be built and tagged by

```bash
$ cd /path/to/<service>/
$ docker build . -t mendersoftware/<service>:master
```

And for an Enterprise repository the steps would be

```bash
$ cd /path/to/<enterprise-service>/
$ docker build . -t registry.mender.io/mendersoftware/<service>:master
```

#### Example -- Running with a Custom Client

For building a custom client the approach is a little different, due to the fact
that the client comes bundles with a Yocto image. Therefore, in order to build
and run a custom client with the integration test setup, first build a Yocto
image, containing the custom client. Then, build a Docker image containing this
client by

```bash
$ cd /path/to/yocto/dir
$ source oe-init-build-env
$ bitbake core-image-full-cmdline
$ cd /path/to/meta-mender
$ cd meta-mender-qemu/docker
$ ./build-docker qemux86-64 -t mendersoftware/mender-client-qemu:master
```

Also remember to add the custom sources to the yocto `conf/local.conf` file,
which for the Mender client is

> 'conf/local.conf'
```bash
.
.
.
PREFERRED_VERSION_pn-mender = "master-git%"
EXTERNALSRC_pn-mender = "$GOPATH"
```

And for Mender-Artifact

> 'conf/local.conf'
```bash
.
.
.
PREFERRED_VERSION_pn-mender-artifact = "master-git%"
EXTERNALSRC_pn-mender-artifact = "$GOPATH"
PREFERRED_VERSION_pn-mender-artifact-native = "master-git%"
EXTERNALSRC_pn-mender-artifact-native = "$GOPATH"
```

> Remember to add your '$GOPATH' in the conf file, it is not taken from the environment.


-------------------------------------------------------------------------------

## Known Issues

#### SSH
Since we attempting to SSH into the virtual mender device, before the OS is up
and running, you may see errors such as:

`Fatal error: Needed to prompt for a connection or sudo password (host:
172.18.0.6:8822), but abort-on-prompts was set to True Aborting.`

These can simply be ignored.


#### OS X

Currently, running integration tests on OS X is not straight forward due to:
https://github.com/docker/docker/issues/22753


## Tips and Tricks

Before running the tests in the VM, remove the leftover `pycache` and `pyc`
files, before testing.

