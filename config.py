import os

from furl import furl

DATABASE_NAME = os.environ.get("DATABASE_NAME")
DATABASE_USER = os.environ.get("DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")

DATABASE_URI = furl(
    scheme="postgresql",
    username=DATABASE_USER,
    password=DATABASE_PASSWORD,
    host="localhost",
    path=DATABASE_NAME,
).url
