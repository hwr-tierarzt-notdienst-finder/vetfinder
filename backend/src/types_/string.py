import re
from collections.abc import Callable
from typing import Literal, NoReturn, ForwardRef, Iterable, TypeVar

_TStr = TypeVar("_TStr", bound=str)

_StringMatcherStrType = Literal[
    "full",
    "contains",
    "start",
    "end",
    "regex",
    "regex:full",
    "regex:start",
    "regex:end",
]

HowManyShouldMatch = Literal[
    "all",
    "any",
    "exactly_one"
]
_MatcherDecisionTreeNotNode = tuple[Literal["not"], ForwardRef("Matcher")]
_MatcherDecisionTreeMultipleNode = tuple[HowManyShouldMatch, Iterable[ForwardRef("Matcher")]]
_MatcherDecisionTree = _MatcherDecisionTreeNotNode | _MatcherDecisionTreeMultipleNode

Matcher = (
        str
        | tuple[_StringMatcherStrType, str]
        | _MatcherDecisionTree
        | re.Pattern[str]
        | Callable[[_TStr], bool | _TStr | NoReturn]
)
