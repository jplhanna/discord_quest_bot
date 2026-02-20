from typing import Final

from fixit import InvalidTestCase
from fixit import LintRule
from fixit import ValidTestCase
from libcst import AnnAssign
from libcst import Annotation
from libcst import Assign
from libcst import AssignTarget
from libcst import ClassDef
from libcst import ImportAlias
from libcst import ImportFrom
from libcst import Index
from libcst import Module
from libcst import Name
from libcst import SimpleStatementLine
from libcst import Subscript
from libcst import SubscriptElement
from libcst import matchers as m


class ConstantsTypedWithFinalRule(LintRule):
    AUTOFIX: Final = True
    VALID: list = [
        ValidTestCase('CONSTANT: Final[str] = "constant"'),
        ValidTestCase("CONSTANT: Final[int] = 1"),
        ValidTestCase("CONSTANT: Final = 2.5"),
        ValidTestCase("CONSTANTS: dict = {}"),
        ValidTestCase("CONSTANTS: Final[dict] = {}"),
    ]

    INVALID: list = [
        InvalidTestCase('CONSTANT = "constant"'),
        InvalidTestCase("CONSTANT = 1"),
    ]

    MESSAGE: Final = "Capitalized variables are intended as constants, and should be annotated with Final"

    def __init__(self):
        super().__init__()
        self.is_constant = False
        self.has_annotation = False
        self.can_ignore = False
        self.has_final_import = False
        self.needs_final_import = False

    def visit_Module(self, node: "Module") -> None:
        matched = m.matches(
            node,
            m.Module(
                body=[
                    m.ZeroOrMore(),
                    m.AtLeastN(
                        m.SimpleStatementLine(body=[m.ImportFrom(names=[m.ImportAlias(name=m.Name("Final"))])]), n=1
                    ),
                    m.ZeroOrMore(),
                ],
            ),
        )
        if not self.has_final_import and matched:
            self.has_final_import = True

    def leave_Module(self, original_node: "Module") -> None:
        if not self.has_final_import and self.needs_final_import:
            new_import = SimpleStatementLine(
                body=[ImportFrom(module=Name("typing"), names=[ImportAlias(name=Name("Final"))])]
            )
            self.report(
                original_node,
                "Current file has incorrectly typed constants and does not have the final import",
                replacement=Module(
                    body=[new_import, *original_node.body], header=original_node.header, footer=original_node.footer
                ),
            )
        self.needs_final_import = False
        self.has_final_import = False

    def visit_ClassDef(self, node: "ClassDef") -> bool | None:
        # ignore class attributes of enums since they can't be typed
        if m.matches(node, m.ClassDef(bases=[m.AtLeastN(m.Arg(value=m.Name(m.MatchRegex(".*Enum.*"))), n=1)])):
            self.can_ignore = True

    def leave_ClassDef(self, _: "ClassDef") -> None:
        self.can_ignore = False

    def visit_AssignTarget(self, node: "AssignTarget") -> bool | None:
        attr = m.extract(
            node.target,
            m.SaveMatchedNode(m.Name(m.DoNotCare()), "name") | m.Attribute(attr=m.SaveMatchedNode(m.Name(), "name")),
        )
        if attr and attr["name"].value.isupper() and len(attr["name"].value) > 1:
            self.is_constant = True

    def leave_Assign(self, original_node: "Assign") -> None:
        if not self.can_ignore and self.is_constant and not self.has_annotation:
            self.report(
                original_node,
                f"{original_node.targets[0].target.value} is an all caps variable "
                "but does not have a Final type Annotation",
                replacement=AnnAssign(
                    target=original_node.targets[0].target,
                    annotation=Annotation(annotation=Name("Final")),
                    value=original_node.value,
                ),
            )
            self.needs_final_import = True
        self.is_constant = False

    def visit_AnnAssign_annotation(self, node: "AnnAssign") -> None:
        self.has_annotation = True
        # Mutable constants can be non-final as they are used for dependency injection
        if self.is_constant and m.matches(
            node.annotation,
            ~(
                m.Annotation(
                    annotation=m.Subscript(value=m.Name("Final")) | m.Name("Final") | m.Name("list") | m.Name("dict")
                )
            ),
        ):
            self.report(
                node.annotation,
                f"{node.target.value} looks like a constant, but is not typed with Final or a mutable type",
                replacement=Annotation(
                    annotation=Subscript(
                        value=Name("Final"), slice=[SubscriptElement(slice=Index(value=node.annotation.annotation))]
                    )
                ),
            )
            self.needs_final_import = True

    def leave_AnnAssign_annotation(self, _: "AnnAssign") -> None:
        self.has_annotation = False
