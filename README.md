# Suikinkutsu

A tool for developer efficiency when they are on the road, using container-based infrastructure, because we all cook 
with water.

[![Build](https://github.com/MrMatAP/suikinkutsu/actions/workflows/build.yml/badge.svg)](https://github.com/MrMatAP/suikinkutsu/actions/workflows/build.yml)
[![CodeQL](https://github.com/MrMatAP/suikinkutsu/actions/workflows/codeql.yml/badge.svg)](https://github.com/MrMatAP/suikinkutsu/actions/workflows/codeql.yml)

> Before you say something, I know the code in here is not ready. I work on this shortly before or while I'm on the road.
> Since I have a life and it's something primarily meant to be useful for me, expect long iterations for this to get
> better... It's nothing at enterprise-grade and likely won't ever be.

## Background

Suikinkutsu has the following goals:

* **Provide useful "personal" infrastructure for testing and experimentation.** "Personal" in this context does not 
  necessarily mean "local" because Suikinkuts should also allow you to spin up personal infrastructure in any cloud or 
  shared hosting platform available to you, such as a cloud and remote Kubernetes cluster. Suikinkutsu currently focuses 
  on local Docker and Rancher (using nerdctl) though. There is very early support for abstracting Kubernetes 
  deployments (it will scan and look for instances it created in clusters looked up in your local `~/.kube/config`, 
  which is why `sk platform list` may take longer than expected, especially when those clusters are unavailable).
* **Help with secrets management**. Suikinkutsu will generate secrets and store them in a configurable location outside 
  your repository whenever you spin up an instance of something that requires them. These secrets can then be picked 
  up by your testsuite.
* **Offer simplified, consistent interaction with instances**. I find it inconvenient to spin up a container just for 
  client 
  utilities to interact with whatever instances I spun up. You have to learn how to do that when all that you want 
  is to spin up some account in PostgreSQL to test with or create a Kafka topic. The aim here is to have Suikinkutsu do 
  this for you (e.g. `sk kafka up; sk kafka topic create -n kafka_instance_name -t topic_name`).
* **Allow for sharing configurations**. The expected workflow for a developer is to experiment with something using 
  their own "personal" infrastructure on their feature branch. That developer will eventually want to share her 
  insights with a buddy. Configuration on what infrastructure is needed (including what accounts and data it should 
  contain) is meant to be persisted in a `Recipe` within the repository. Such recipes avoid lengthy explanations to 
  fellow developers what and how to set it up. Recipes are currently still pretty non-functional.

## How to install this

Clone this repository and install the Python package. At this stage you will likely want to install this in a virtual
environment. You can also install the Python package into your home directory directly (`pip install --user`) to
avoid having to remember activating the virtual environment before executing `sk`.

```shell
# Create and activate a virtual environment (optional, but recommended)
$ python -m virtualenv /path/to/virtualenv/suikinkutsu
$ . /path/to/virtualenv/suikinkutsu/bin/activate

# Build and install Kaso Mashin
$ pip install -U /path/to/cloned/sources/dev-requirements.txt
$ python -m build -n --wheel
$ pip install ./dist/*.whl

# Validate whether it worked
$ sk -h
```

### How to update this

At this point Suikinkutsu is updated from its sources in git. It will be published in the regular Python Packaging Index
by the time it reached a bit more maturity.

```shell
# Navigate to your clone of the Suikinkutsu sources and update
$ git pull

# Activate the virtual environment in which it is currently installed
$ . /path/to/virtualenv/suikinkutsu/bin/activate

# Install and update dependencies, then build and install
$ pip install -U /path/to/cloned/sources/dev-requirements.txt
$ python -m build -n --wheel
$ pip install ./dist/*.whl

# Validate whether it worked
$ sk -h
```

### Configuration

It is sometimes confusing why and where-from your tools are configured. Suikinkutsu will therefore tell you whether a 
configuration is a default, from a config file, the CLI or from an environment variable in `sk config show`. The 
philosophy on precendence is as follows, from lowest to highest:

* Defaults
* An entry in the config file overrides the default
* An environment variable overides an entry in the config file
* A command line parameter overrides an environment variable

The reason for this philosophy is based on the effort required to establish the configuration. It is considered to 
require more effort to set an environment variable than to override it for a particular run of the tool on the CLI.

>*NOTE*: Suikinkutsu used to be called 'Water', but that name was taken on Pypi and we haven't gotten around to fix
> the config system yet.

| Configuration | Environment Variable   | CLI Argument | Default                           | Description                                                                                                           |
|---------------|------------------------|--------------|-----------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| config_file   | WATER_CONFIG_FILE      | -c           | ~/.water                          | Overall configuration file for water itself                                                                           |
| config_dir    | WATER_CONFIG_DIR       | -d           | ~/etc                             | Base path into which app-specific config files (with secrets) are written                                             |
| output        | WATER_DEFAULT_OUTPUT   | -o           | human                             | Output format. One of 'human', 'json' or 'yaml'                                                                       |
| platform      | WATER_DEFAULT_PLATFORM | -p           | nerdctl                           | Default platform in which instances are created. These are auto-discovered and even the default may not be available. |
| recipe_file   | WATER_RECIPE           | TODO         | <PROJECT>/Recipe                  | File (within repository) in which the overall recipe for instances is stored (currently non-functional)               |
| secrets_file  | WATER_SECRETS_FILE     | -s           | <WATER_CONFIG_DIR>/<PROJECT>.json | App-specific config file (with secrets)                                                                               |

## How to use this

Suikinkutsu is meant to have a similar concept to invocation as the Azure CLI has.

* Show configuration and where it comes from: `sk config show`
* Show available blueprints: `sk blueprint list`
* Show available platforms: `sk platform list`
* Show instances that were created: `sk instance list`
* Spin up a PostgreSQL instance with the default name ('pg'): `sk pg create`
* Spin up a named (second) PostgreSQL instance: `sk pg up -n test`
* Get help on PostgreSQL customisation commands: `sk pg -h`
* Get help on PostgreSQL role commands: `sk pg role -h`
* Get help on the PostgreSQL role creation command: `sk pg role create -h`
* Create a PostgreSQL role: `sk pg role create -n pg -r testrole -p foobar --create-schema`


## Known issues & Limitations

* If you get encoding errors on Windows while testing the outputs in PyCharm but the tests succeed in the normal 
  Terminal console then check what the default encoding is for the PyCharm console. Chances are that it's not set to 
  UTF-8.
