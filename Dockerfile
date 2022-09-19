FROM python:alpine3.14

USER root

COPY resources/consultaDatosTrivyImage.py /opt/
COPY resources/consultaDatosTrivyFile.py /opt/
COPY resources/consultaDatosMarkDown.py /opt/
COPY resources/consultaDatosHadolint.py /opt/
COPY resources/consultaDatosApplications.py /opt/

RUN apk add --update --no-cache build-base python3-dev python3 libffi-dev libressl-dev postgresql-dev curl 


RUN pip install regex requests psycopg2-binary pytz  elementpath pyyaml


