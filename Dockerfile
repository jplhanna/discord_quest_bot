FROM python:3.10.4 as base
MAINTAINER JP Hanna "jpl.hanna@gmail.com"
WORKDIR /app/
COPY . /app/

FROM base as install-pipenv
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
RUN pipenv install --system --deploy --ignore-pipfile

# Install application into container
ENV PYTHONPATH "{$PYTHONPATH}:/app/"
