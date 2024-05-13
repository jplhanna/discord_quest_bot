from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from litestar import Controller
from litestar import get
from litestar import post
from litestar.exceptions import NotFoundException
from pydantic import UUID4

from src.api.endpoints import LOGIN_ROUTE
from src.api.endpoints import USER_ROUTE
from src.api.schemas import UserCreateSchema
from src.api.schemas import UserLoginSchema
from src.containers import Container
from src.models import User
from src.services import UserService


class UserAPI(Controller):
    path = USER_ROUTE

    @inject
    @get(path="/{user_id:uuid}")
    async def get_user_by_id(self, uuid: UUID4, user_service: UserService = Provide[Container.user_service]) -> User:
        user = await user_service.get_user_by_uuid(uuid)
        if not user:
            raise NotFoundException
        return user

    @inject
    @post(dto=UserCreateSchema)
    async def register_user(self, user: User, user_service: UserService = Provide[Container.user_service]) -> User:
        await user_service.create_litestar_user(user)
        return user


class LoginAPI(Controller):
    path = LOGIN_ROUTE

    @post(dto=UserLoginSchema)
    def login_user(self, user: User) -> User:
        # TODO write up security functionality
        return user


REGISTERED_APIS: list[type[Controller]] = [UserAPI]
