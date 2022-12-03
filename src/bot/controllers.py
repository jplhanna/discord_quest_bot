from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from discord.ext.commands import Context

from src.bot.constants import ALREADY_REGISTERED_MESSAGE
from src.bot.constants import NEW_USER_MESSAGE
from src.bot.constants import REGISTER_FIRST_MESSAGE
from src.containers import Container
from src.exceptions import BaseQuestException
from src.exceptions import NoIDProvided
from src.exceptions import QuestAlreadyAccepted
from src.exceptions import QuestDNE
from src.helpers.message_helpers import format_quest_board
from src.services import ExperienceTransactionService
from src.services import QuestService
from src.services import UserService


@inject
async def check_and_register_user(ctx: Context, user_service: UserService = Provide[Container.user_service]) -> str:
    discord_id = ctx.author.id
    if not discord_id:
        raise NoIDProvided()
    if await user_service.get_user_by_discord_id(discord_id):
        return ALREADY_REGISTERED_MESSAGE
    await user_service.create_user(discord_id=discord_id)
    return NEW_USER_MESSAGE


@inject
async def add_quest_to_user(
    ctx: Context,
    quest_name: str,
    quest_service: QuestService = Provide[Container.quest_service],
    user_service: UserService = Provide[Container.user_service],
) -> str:
    user = await user_service.get_user_by_discord_id(ctx.author.id)
    if not user:
        return REGISTER_FIRST_MESSAGE
    try:
        res = await quest_service.accept_quest_if_available(user, quest_name)
    except (QuestDNE, QuestAlreadyAccepted) as quest_error:
        res = quest_error.message
    return res


@inject
async def get_quest_list_text(quest_service: QuestService = Provide[Container.quest_service]) -> str:
    quests = await quest_service.get_all_quests()
    message = format_quest_board(quests)
    return message


@inject
async def complete_quest_for_user(
    ctx: Context,
    quest_name: str,
    user_service: UserService = Provide[Container.user_service],
    quest_service: QuestService = Provide[Container.quest_service],
    xp_service: ExperienceTransactionService = Provide[Container.xp_service],
) -> str:
    user = await user_service.get_user_by_discord_id(ctx.author.id)
    if not user:
        return REGISTER_FIRST_MESSAGE

    try:
        quest = await quest_service.complete_quest_if_available(user, quest_name)
    except BaseQuestException as quest_error:
        return quest_error.message
    xp_transaction = await xp_service.earn_xp_for_quest(user, quest)
    return f"You have successfully completed {quest.name} and earned {xp_transaction.experience}"
