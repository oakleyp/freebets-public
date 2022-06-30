#!/usr/bin/env bash

set -x

mypy app --show-traceback
black app --check
isort --recursive --check-only app
flake8
