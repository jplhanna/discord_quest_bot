from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from discord.ext.commands import Context

from src.bot.constants import ALREADY_REGISTERED_MESSAGE
from src.bot.constants import NEW_USER_MESSAGE
from src.bot.constants import NO_MENU_THIS_WEEK_MESSAGE
from src.bot.constants import REGISTER_FIRST_MESSAGE
from src.bot.constants import SERVER_ONLY_BAD_REQUEST_MESSAGE
from src.constants import DayOfWeek
from src.containers import Container
from src.exceptions import NoIDProvided
from src.helpers.message_helpers import format_quest_board
from src.quests import ExperienceTransactionService
from src.quests import QuestService
from src.quests.exceptions import BaseQuestException
from src.quests.exceptions import QuestAlreadyAccepted
from src.quests.exceptions import QuestDNE
from src.services import UserService
from src.tavern import TavernService
from src.tavern.exceptions import NoMenuItemFoundError


@inject
async def check_and_register_user(ctx: Context, user_service: UserService = Provide[Container.user_service]) -> str:
    discord_id = ctx.author.id
    if not discord_id:
        raise NoIDProvided
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
    return format_quest_board(quests)


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
    except (BaseQuestException, QuestDNE) as quest_error:
        return quest_error.message
    xp_transaction = await xp_service.earn_xp_for_quest(user, quest)
    return f"You have successfully completed {quest.name} and earned {xp_transaction.experience}"


@inject
async def get_tavern_menu(ctx: Context, tavern_service: TavernService = Provide[Container.tavern_service]) -> str:
    if not ctx.guild:
        return SERVER_ONLY_BAD_REQUEST_MESSAGE
    menu = await tavern_service.get_this_weeks_menu(ctx.guild.id)
    if not menu:
        return NO_MENU_THIS_WEEK_MESSAGE
    menu_str = f"Menu for the week of {menu.start_date.strftime('%b %d, %Y')}"
    for day, items in menu.grouped_items.items():
        menu_str += f"\n**{day.name.title()}**:"
        if not items:
            menu_str += "\n  No items available."
        for item in items:
            menu_str += f"\n  - {item.food.capitalize()}"
    return menu_str


@inject
async def upsert_tavern_menu(
    ctx: Context,
    item_name_str: str,
    day_of_week: DayOfWeek,
    tavern_service: TavernService = Provide[Container.tavern_service],
) -> str:
    if not ctx.guild:
        return SERVER_ONLY_BAD_REQUEST_MESSAGE
    server_id = ctx.guild.id
    menu = await tavern_service.get_this_weeks_menu(server_id)
    if not menu:
        menu = await tavern_service.create_menu_for_week(server_id)
    await tavern_service.insert_menu_item(menu, item_name_str, day_of_week)
    return "Item added"


@inject
async def remove_from_tavern_menu(
    ctx: Context,
    item_name_str: str,
    day_of_week: DayOfWeek | None,
    tavern_service: TavernService = Provide[Container.tavern_service],
) -> str:
    if not ctx.guild:
        return SERVER_ONLY_BAD_REQUEST_MESSAGE
    menu = await tavern_service.get_this_weeks_menu(ctx.guild.id)
    if not menu:
        return NO_MENU_THIS_WEEK_MESSAGE

    try:
        await tavern_service.delete_menu_item(menu, item_name_str, day_of_week)
    except NoMenuItemFoundError:
        day_of_week_error_text = f" on {day_of_week.name.lower()}" if day_of_week else ""
        return f"{item_name_str.capitalize()} could not be found{day_of_week_error_text} in this week's menu."

    return "Item successfully removed"
