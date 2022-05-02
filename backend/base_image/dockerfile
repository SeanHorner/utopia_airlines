# For a reasoning on Debian slim pre-built Python image over using Alpine look here:
# https://pythonspeed.com/articles/alpine-docker-python/
#
# tl;dr:
#   Alpine's use of the musl instead of glibc makes for headaches trying to work with
#   python, especially some popular (and C-heavy) libraries.

# syntax=docker/dockerfile:1
FROM python:3.9.9-slim

LABEL maintainer="sean.horner@smoothstack.com"
LABEL project="utopia_airlines"

RUN useradd utopian

WORKDIR /home/utopian

# setting up the virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Copying in and applying the project requirements.
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Installing mysql helper programs
RUN apt-get update
RUN apt-get -y install default-libmysqlclient-dev
RUN apt-get -y install build-essential
