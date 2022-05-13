FROM python:3.10.4 as base
MAINTAINER JP Hanna "jpl.hanna@gmail.com"

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV WORKON_HOME /local_server
ENV PIPENV_PROFILE /Pipfile


RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --ignore-pipfile

# Install application into container
COPY . .
