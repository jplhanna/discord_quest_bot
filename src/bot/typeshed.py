from collections.abc import Callable
from collections.abc import Coroutine
from typing import TYPE_CHECKING
from typing import Concatenate
from typing import ParamSpec

if TYPE_CHECKING:
    from discord.ext.commands import Context
    from discord.ext.commands import HybridCommand
    from mypy_extensions import DefaultNamedArg
    from mypy_extensions import NamedArg

    P = ParamSpec("P")
    CommandFunc = (
        Callable[Concatenate[Context, P], Coroutine]
        | Callable[[Context], Coroutine]
        | Callable[[Context, NamedArg(str, "quest_name")], Coroutine]
    )
    CommandRegisterType = Callable[
        [NamedArg(str, "name"), NamedArg(str, "help"), DefaultNamedArg(list[str], "aliases")],
        Callable[[CommandFunc], HybridCommand],
    ]
else:
    CommandRegisterType = Callable
