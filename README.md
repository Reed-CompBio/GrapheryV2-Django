# Graphery Django Backend

## Intro

This is the backend of Graphery. It provides the database storage for all tutorials, networks, code, and pre-compiled execution results. GraphQL API is used to support communication with the frontend.

The backend is still under development and testing.

## Install Test Environment

### With Poetry and Docker

There is a pre-configured test environment located under `setups/test-env/`. It is built with [Docker](https://www.docker.com/) and therefore docker has to be present to run it. However, you can use it without docker if can setup Postgresql and Redis locally, and modify the Django settings accordingly.

The project requirement is managed by [Poetry](https://www.poetry.io/). The current requirement needs the latest beta of poetry so you need to use `poetry self update --preview` to update it. Once that's set, you can follow the commands below.

```shell
poetry install --with dev
mkdir -p ./setups/test-env/volumes/postgre-data
mkdir -p ./setups/test-env/volumes/redis-data
docker-compose -f ./setups/test-env/docker-compose.yml up --build -d
poetry run python ./graphery/manage.py migrate
poetry run python ./graphery/manage.py runserver
```

Some features like providing remote execution will need the [`GrapheryExecutor`](https://github.com/Reed-CompBio/GrapheryExecutor) server module. Please check out the README of that repository for more information.


### With Pycharm

There are pre-configured run commands located under `.run/` and PyCharm can identify and list them in its interface. Click run `dev` Django server will do the same thing.


## Install Production Environment

Please follow the instructions provided by Django and setup production Postgresql and Redis environment accordingly. More project specific instructions will be updated soon.


## Design and Documentation

The documentations are located [here](https://docs.graphery.reedcompbio.org/). It's still under development, so many things are not documented yet.


## Contributing

### Issues
Please don't be hesitating to report bugs or feature requests through the Issues page. For more urgent/private reports like security risks, please send emails to [here](mailto:graphery@reed.edu).

### PR
Please run `pre-commit` to check the code style before committing. More specific code conduct, style guidelines, and CI will be provided in the future.
