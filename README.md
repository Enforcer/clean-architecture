# Implementing the Clean Architecture - Auctions
Example project used in the book [Implementing the Clean Architecture](https://leanpub.com/implementing-the-clean-architecture)

[![Implementing the Clean Architecture cover](docs/cover.png)](https://leanpub.com/implementing-the-clean-architecture)

## Discord server

[![Join our Discord server!](https://invidget.switchblade.xyz/cDyDKv2VsY)](http://discord.gg/cDyDKv2VsY)

## Build status
[![CircleCI](https://circleci.com/gh/Enforcer/clean-architecture.svg?style=svg)](https://app.circleci.com/pipelines/github/Enforcer/clean-architecture?branch=master) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Working with the repo
Pycharm - mark each package as Sources Root.
![Marking directories as source root in PyCharm](docs/marking_as_sources_root.png)
Console - `make dev` to install each subpackage in editable mode.

## Working with docker containers
```bash
# Start everything
docker-compose up --build

# Black formatting
docker-compose exec -T app black -l 120 ./
# isort
docker-compose exec -T app isort --recursive ./
# flake8 checks
docker-compose exec -T app flake8 --max-line-length 120 ./
```


