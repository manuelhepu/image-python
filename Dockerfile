FROM python:3.11-alpine3.17

USER root

COPY resources/consultaDatosTrivyImage.py /opt/
COPY resources/consultaDatosTrivyFile.py /opt/
COPY resources/consultaDatosMarkDown.py /opt/
COPY resources/consultaDatosHadolint.py /opt/
COPY resources/consultaDatosApplications.py /opt/

# Instalación paqueteria
RUN apk add --update --no-cache build-base python3-dev python3 libffi-dev libressl-dev postgresql-dev curl 

# Instalación modulos python
RUN pip install regex requests psycopg2-binary pytz  elementpath pyyaml bs4 lxml

# Instalación herramienta yq
RUN wget https://github.com/mikefarah/yq/releases/download/v4.26.1/yq_linux_amd64 -O /usr/bin/yq &&  chmod +x /usr/bin/yq
