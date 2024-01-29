from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Annotated
from typing import Literal
from typing import TypeVar

from pydantic import BaseModel
from pydantic import StringConstraints
from sqlalchemy import ColumnElement
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql import FromClause
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.elements import Label
from sqlalchemy.sql.functions import Function
from sqlalchemy.sql.selectable import CTE

if TYPE_CHECKING:
    from src.models import CoreModelMixin


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

SQLLogicType = BinaryExpression | BooleanClauseList | bool | ColumnElement["bool"]
JoinOnType = type["CoreModelMixin"] | AliasedClass | RelationshipProperty


@dataclass
class JoinStruct:
    join_model: JoinOnType
    join_on: SQLLogicType | RelationshipProperty | None = field(default=None)
    use_outer_join: bool = field(default=False)

    def get_join_data(self) -> tuple[JoinOnType] | tuple[JoinOnType, SQLLogicType | RelationshipProperty]:
        if self.join_on is not None:
            return self.join_model, self.join_on
        return (self.join_model,)

    def get_join_func(self) -> Literal["outerjoin", "join"]:
        if self.use_outer_join:
            return "outerjoin"
        return "join"


JoinListType = Sequence[
    FromClause
    | JoinStruct
    | tuple[JoinOnType, SQLLogicType | RelationshipProperty]
    | tuple[CTE, SQLLogicType]
    | InstrumentedAttribute
]

EntitiesType = Mapped | Label | type["CoreModelMixin"] | Function
BaseModelType = TypeVar("BaseModelType", bound="CoreModelMixin")


class MixinData(BaseModel):
    back_populates: str | None = None
    index: bool = False
