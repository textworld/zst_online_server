#!/bin/bash

export PYTHONOPTIMIZE=1
celery -A zst_project worker -l info
