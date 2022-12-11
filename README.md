# water

A tool for developer efficiency when they are on the road, using container-based infrastructure, because we all cook 
with water.

[![Build](https://github.com/MrMatAP/suikinkutsu/actions/workflows/build.yml/badge.svg)](https://github.com/MrMatAP/suikinkutsu/actions/workflows/build.yml)

> Before you say something, I know the code in here is shit. I work on this shortly before or while I'm on the road.
> Since I have a life and it's something primarily meant to be useful for me, expect long iterations for this to get
> better... It's nothing at enterprise-grade and likely won't ever be.

Water has the following goals:

* **Provide useful "personal" infrastructure for testing and experimentation.** "Personal" in this context does not 
  necessarily mean "local" because water should also allow you to spin up personal infrastructure in any cloud or 
  shared hosting platform available to you, such as a cloud and remote Kubernetes cluster. Water currently focuses 
  on local Docker and Rancher (using nerdctl) though. There is very early support for abstracting Kubernetes 
  deployments (it will scan and look for instances it created in clusters looked up in your local `~/.kube/config`, 
  which is why `water platform list` may take longer than expected, especially when those clusters are unavailable).
* **Help with secrets management**. Water will generate secrets and store them in a configurable location outside 
  your repository whenever you spin up an instance of something that requires them. These secrets can then be picked 
  up by your testsuite.
* **Offer simplified, consistent interaction with instances**. I find it inconvenient to spin up a container just for 
  client 
  utilities to interact with whatever instances I spun up. You have to learn how to do that when all that you want 
  is to spin up some account in PostgreSQL to test with or create a Kafka topic. The aim here is to have water do 
  this for you (e.g. `water kafka up; water kafka topic create -n kafka_instance_name -t topic_name`).
* **Allow for sharing configurations**. The expected workflow for a developer is to experiment with something using 
  their own "personal" infrastructure on their feature branch. That developer will eventually want to share her 
  insights with a buddy. Configuration on what infrastructure is needed (including what accounts and data it should 
  contain) is meant to be persisted in a `Recipe` within the repository. Such recipes avoid lengthy explanations to 
  fellow developers what and how to set it up. Recipes are currently still pretty non-functional.

## How to install this

Navigate to the [GitLab pypi package registry](https://gitlab.com/mrmatorg/water/-/packages/) for water and click on 
the desired release to be installed. The resulting page will show the necessary commands.

It boils down to the following. It makes sense to install water into a virtualenv before committing to using it. If 
you end up being a fan and use it all them time, consider adding the `--user` flag to pip so it is installed user-wide
and accessible from any other project you may be working on.

### If you have a GitLab personal access token

Note that `__token__` is a literal, but `<your_personal_token>` must be replaced with your personal access token. 
GitLab states you ought to use `--extra-index-url`, but **you must adjust the command to say `--index-url`** so the
repo becomes the primary source of package name resolution. This is because the main pypi index contains other projects
called water which will be found first otherwise.

```shell
$ pip install suikinkutsu --index-url https://__token__:<your_personal_token>@gitlab.com/api/v4/projects/36380957/packages/pypi/simple
```

### If you don't have a GitLab personal access token

If you don't have a personal access token in GitLab (or you can't be bothered) then download the wheel from this page
and install it as follows:

```shell
$ pip install /path/to/downloaded/wheel.whl
```

## How to use this

Water is meant to have a similar concept to invocation as the Azure CLI has.

* Show configuration and where it comes from: `water config show`
* Show available blueprints: `water blueprint list`
* Show available platforms: `water platform list`
* Show instances that were created: `water instance list`
* Spin up a PostgreSQL instance with the default name ('pg'): `water pg create`
* Spin up a named (second) PostgreSQL instance: `water pg up -n test`
* Get help on PostgreSQL customisation commands: `water pg -h`
* Get help on PostgreSQL role commands: `water pg role -h`
* Get help on the PostgreSQL role creation command: `water pg role create -h`
* Create a PostgreSQL role: `water pg role create -n pg -r testrole -p foobar --create-schema`

### Configuration

It is sometimes confusing why and where-from your tools are configured. Water will therefore tell you whether a 
configuration is a default, from a config file, the CLI or from an environment variable in `water config show`. The 
philosophy on precendence is as follows, from lowest to highest:

* Defaults
* An entry in the config file overrides the default
* An environment variable overides an entry in the config file
* A command line parameter overrides an environment variable

The reason for this philosophy is based on the effort required to establish the configuration. It is considered to 
require more effort to set an environment variable than to override it for a particular run of the tool on the CLI.

| Configuration | Environment Variable   | CLI Argument | Default                           | Description                                                                                                           |
|---------------|------------------------|--------------|-----------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| config_file   | WATER_CONFIG_FILE      | -c           | ~/.water                          | Overall configuration file for water itself                                                                           |
| config_dir    | WATER_CONFIG_DIR       | -d           | ~/etc                             | Base path into which app-specific config files (with secrets) are written                                             |
| output        | WATER_DEFAULT_OUTPUT   | -o           | human                             | Output format. One of 'human', 'json' or 'yaml'                                                                       |
| platform      | WATER_DEFAULT_PLATFORM | -p           | nerdctl                           | Default platform in which instances are created. These are auto-discovered and even the default may not be available. |
| recipe_file   | WATER_RECIPE           | TODO         | <PROJECT>/Recipe                  | File (within repository) in which the overall recipe for instances is stored (currently non-functional)               |
| secrets_file  | WATER_SECRETS_FILE     | -s           | <WATER_CONFIG_DIR>/<PROJECT>.json | App-specific config file (with secrets)                                                                               |

## How to hack on this

* If you get encoding errors on Windows while testing the outputs in PyCharm but the tests succeed in the normal 
  Terminal console then check what the default encoding is for the PyCharm console. Chances are that it's not set to 
  UTF-8.

### How to build this

This project uses the [PEP517 build method](https://peps.python.org/pep-0517/). But it also uses a method for 
CI-controlled auto-versioning that relies on build-time access to a Python-module at the root of the repository for 
relaying the 'MRMAT_VERSION' environment variable containing the version string into the build-mechanism via 
`ci/__init__.py`. This build-time only module is specifically excluded from the runtime package the build process 
produces.

The 'MRMAT_VERSION' environment variable is constructed by the CI pipeline, which defines 'MAJOR' and 'MINOR' version
numbers to be manually adjusted as needed. Modification of these are deliberately expected to require a commit to 
the repository. The MICRO version is based on the ever-increasing unique number of pipeline runs for the project, 
for which we rely on the CI system. In GitLab, the 'MRMAT_VERSION' is constructed as the first part of the build job 
which also recognises whether we are making a release through convention that any merge into the main branch is such 
a release. 

Since `ci/__init__.py` is not part of the main sources of the project, you must enable Python to find it during the 
build by temporarily setting PYTHONPATH to the root of your repository. A build consequently looks as follows:

```shell
# Navigate to the root of the repository
$ PYTHONPATH=$(pwd) python -m build -n --wheel
```

Note that the `-n` option implies that the projects dependencies are installed into the current environment you are 
in. Omit this in order not to pollute your environment.

Note that `setup.cfg` only includes runtime requirements for the project. All build-time requirements can easily be 
installed via `pip install -r requirements.txt`. This is particularly useful when executing all this from within an IDE.
