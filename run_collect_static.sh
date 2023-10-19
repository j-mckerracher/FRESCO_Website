#!/bin/bash
echo "Using Python version:"
$VENV/bin/python --version
$VENV/bin/python manage.py collectstatic --noinput