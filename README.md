# Discord Quest bot

A discord bot built in python. I am using this to test my skills.
The current plan is to create a bot which tracks user tasks and reward you for completing tasks.

All of these tasks and progress are tracked with a postgres db which maps discord users to db users.

## Setup

To install and run this bot locally, it is currently required to clone this repo.

```commandline
git clone git@github.com:jplhanna/local_work.git
```

Add necessary environment variables

```shell
DISCORD_ACCOUNT_TOKEN="account token for you discord bot"
DATABASE_NAME="Name for the database"
DATABASE_USER="Name for user with access to the database"
DATABASE_PASSWORD="Password to the database"
DISCORD_OWNER_ID="The discord id of the owner of the channel you are using."
```

Install all packages and start the server using `Docker` and `docker-compose`

```commandline
docker-compose build backend
docker-compose up backend
```

### Dev setup

If you plan to do development on this bot you must do additional work.

Add the following to your env

```shell
# This is necessary for the integration test suite
TEST_DATABASE_NAME="Name for you test db"
```

And build the rest of the docker setup

```commandline
docker-compose build test-pipeline
docker-compose run test-pipeline pre-commit install
```

You can run any of the test pipelines using

```commandline
docker-compose run test-pipeline <fill in here>
```
