from datetime import date

from discord.ext.commands import FlagConverter
from discord.ext.commands import flag

from constants import ChooseStyle
from constants import DayOfWeek


class RandomChoiceFlag(FlagConverter):
    style: ChooseStyle = ChooseStyle.RANDOM
    day_of_week: DayOfWeek = flag(default=lambda _: DayOfWeek(date.today().weekday()))
