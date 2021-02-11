#!/usr/bin/env bash
export FLASK_APP=application.py
export FLASK_DEBUG=1
export DATABASE_URL=postgres://etrfsjyhdmwult:9b5b9d599e303c30bd329266871f2653016154c8f2cba5c6439022abbe341077@ec2-52-7-168-69.compute-1.amazonaws.com:5432/d4j6denllckr8l
flask run