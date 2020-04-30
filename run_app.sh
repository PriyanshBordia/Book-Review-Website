#!/usr/bin/env bash
export FLASK_APP=application.py
export DATABASE_URL=
flask run --port $PORT --host=$IP
