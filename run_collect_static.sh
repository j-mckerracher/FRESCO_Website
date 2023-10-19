#!/bin/bash
echo "Using Python version:"
python3 --version
python3 manage.py collectstatic --noinput
