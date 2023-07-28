from typing import Callable
from typing import Concatenate
from typing import Coroutine
from typing import ParamSpec

from discord.ext.commands import Context
from discord.ext.commands import HybridCommand
from mypy_extensions import DefaultNamedArg
from mypy_extensions import NamedArg

P = ParamSpec("P")
CommandFunc = (
    Callable[Concatenate[Context, P], Coroutine]
    | Callable[[Context], Coroutine]
    | Callable[[Context, NamedArg(str, "quest_name")], Coroutine]  # noqa: F821
)
CommandRegisterType = Callable[
    [NamedArg(str, "name"), NamedArg(str, "help"), DefaultNamedArg(list[str], "aliases")],  # noqa: F821
    Callable[[CommandFunc], HybridCommand],
]
