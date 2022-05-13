FROM python:3.10.4 as base
MAINTAINER JP Hanna "jpl.hanna@gmail.com"
WORKDIR /app/

RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --system --deploy --ignore-pipfile

# Install application into container
COPY . /app/

ENV PYTHONPATH "{$PYTHONPATH}:/app/"
