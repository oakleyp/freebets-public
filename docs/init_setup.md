# Initial Setup

This assumes that you have the following installed:

- docker
- python >= 3.8

## Secrets/Config

1. Rename/copy the `.env_sample` file in the repo root to `.env` in the same directory
2. In that same file:
    - Replace all passwords in that file with your own unique passwords

## First Run

On the first run, you will need to build the docker images in the stack:
```
$ docker-compose build
```

## Starting the Docker Stack Locally

Run the following:
```
$ docker-compose up -d
```

The service is now live, although you will need to complete at least the `Live Racing` implementation in [Batteries](./design/batteries.md) for bets to be generated. 

See [Development Workflow](./dev_workflow.md) for further instructions once the stack is running.
