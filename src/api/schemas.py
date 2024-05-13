from litestar.contrib.pydantic import PydanticDTO
from litestar.dto import DTOConfig
from litestar.dto import dto_field

from src.models import User
from src.typeshed import NonEmptyString


class UserCreateSchema(PydanticDTO[User]):
    config = DTOConfig(include={"username", "email", "password"})

    username: NonEmptyString
    password = dto_field("write-only")


class UserLoginSchema(PydanticDTO[User]):
    config = DTOConfig(include={"username", "password"})
