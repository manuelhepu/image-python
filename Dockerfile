FROM python:alpine3.14

USER root


RUN apk add --update --no-cache build-base python3-dev python3 libffi-dev libressl-dev postgresql-dev curl 


RUN pip install regex requests psycopg2-binary pytz  elementpath pyyaml bs4 lxml


