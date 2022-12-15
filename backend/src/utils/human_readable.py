import math
from abc import abstractmethod
from collections.abc import Iterable
from copy import copy
from dataclasses import dataclass
from typing import Literal, TypeAlias, Protocol, cast, Any, runtime_checkable, TypeVar, overload, Type, TYPE_CHECKING

QuoteStyle: TypeAlias = Literal[
    "single",
    "double",
    "code"
]
StringModifier: TypeAlias = Literal[
    "quoted:single",
    "double:double",
    "quoted:code"
]
_DecomposedStringModifier = Literal[
                                "quoted"
                            ] | StringModifier
SequenceModifier: TypeAlias = Literal[
                                  "delimiter:,",
                                  "delimiter:|",
                                  "conjunction:and",
                                  "conjunction:or",
                                  "conjunction:and/or",
                              ] | StringModifier
_DecomposedSequenceModifier: TypeAlias = Literal[
                                             "delimiter",
                                             "conjunction"
                                         ] | SequenceModifier | _DecomposedStringModifier


class Error(Exception):
    pass


class UnexpectedType(Error, TypeError):
    pass


class InvalidModifier(Error, ValueError):
    pass


class ModifierAlreadyUsed(Error, ValueError):
    pass


class StringError(Error):
    pass


class InvalidStringModifier(StringError, InvalidModifier):
    pass


class StringModifierAlreadyUsed(StringError, ModifierAlreadyUsed):
    pass


class SequenceError(Error):
    pass


class InvalidSequenceModifier(SequenceError, InvalidModifier):
    pass


class SequenceModifierAlreadyUsed(SequenceError, ModifierAlreadyUsed):
    pass


_STRING_MODIFIERS: set[StringModifier] = {
    "quoted:single",
    "quoted:double",
    "quoted:code",
}
_DECOMPOSED_STRING_MODIFIERS: set[_DecomposedStringModifier] = {
                                                                   "quoted",
                                                               } | _STRING_MODIFIERS

_SEQUENCE_MODIFIER: set[SequenceModifier] = {
                                                "delimiter:,",
                                                "delimiter:|",
                                                "conjunction:and",
                                                "conjunction:or",
                                                "conjunction:and/or",
                                            } | _STRING_MODIFIERS
_DECOMPOSED_SEQUENCE_MODIFIER: set[SequenceModifier] = {
                                                           "conjunction",
                                                       } | _SEQUENCE_MODIFIER


def is_string_modifier(modifier: str) -> bool:
    return modifier in _STRING_MODIFIERS


def _is_decomposed_string_modifier(modifier: str) -> bool:
    return modifier in _DECOMPOSED_STRING_MODIFIERS


def is_sequence_modifier(modifier: str) -> bool:
    return modifier in _SEQUENCE_MODIFIER


def _is_decomposed_sequence_modifier(modifier: str) -> bool:
    return modifier in _DECOMPOSED_SEQUENCE_MODIFIER


@dataclass(frozen=True)
class Config:
    default_quote_style: Literal["single", "double", "code"] = "single"
    default_sequence_delimiter: Literal[",", "|"] | None = ","
    default_sequence_conjunction: Literal["and", "or", "and/or"] | None = None
    default_shorten_sequence_if_longer_than: int | None = 4


@runtime_checkable
class _Named(Protocol):

    __name__: str


_WithStringModificationsSubtype = TypeVar(
    "_WithStringModificationsSubtype",
    bound="WithStringModifications"
)


@runtime_checkable
class WithStringModifications(Protocol):

    def quoted(self, style: QuoteStyle | None = None) -> _WithStringModificationsSubtype: ...

    def single_quoted(self) -> _WithStringModificationsSubtype: ...

    def double_quoted(self) -> _WithStringModificationsSubtype: ...

    def code(self) -> _WithStringModificationsSubtype: ...


_ExtendsStringModifier = TypeVar(
    "_ExtendsStringModifier",
    bound=StringModifier
)
_ExtendsDecomposedStringModifier = TypeVar(
    "_ExtendsDecomposedStringModifier",
    bound=StringModifier
)


_StringModificationBehaviourSubtype = TypeVar(
    "_StringModificationBehaviourSubtype",
    bound="WithStringModifications"
)


class _StringModificationBehaviour(
    WithStringModifications,
    Protocol[_StringModificationBehaviourSubtype, _ExtendsStringModifier, _ExtendsDecomposedStringModifier],
):
    _MODIFIER_ALREADY_USED_ERROR: Type[ModifierAlreadyUsed]

    _config: Config
    _decomposed_modifiers: set[_ExtendsDecomposedStringModifier]

    def modified(
            self,
            modifier: _ExtendsStringModifier
    ) -> _StringModificationBehaviourSubtype:
        copy_ = copy(self)

        return copy_._use_modifier(modifier)

    def quoted(self, style: QuoteStyle | None = None) -> _StringModificationBehaviourSubtype:
        modifier = cast(
            StringModifier,
            f"quoted:{style or self._config.default_quote_style}"
        )

        return self.modified(modifier)

    def single_quoted(self) -> _StringModificationBehaviourSubtype:
        return self.quoted("single")

    def double_quoted(self) -> _StringModificationBehaviourSubtype:
        return self.quoted("double")

    def code(self) -> _StringModificationBehaviourSubtype:
        return self.quoted("code")

    def _use_modifier(self, modifier: _ExtendsStringModifier) -> _StringModificationBehaviourSubtype:
        self._validate_modifier(modifier)

        decomposed_modifier: _ExtendsDecomposedStringModifier | Literal[""] = ""
        for specifier in modifier.split(":"):
            if decomposed_modifier == "":
                decomposed_modifier += specifier
            else:
                decomposed_modifier += f":{specifier}"

            if decomposed_modifier in self._decomposed_modifiers:
                raise self._MODIFIER_ALREADY_USED_ERROR(decomposed_modifier)

            self._decomposed_modifiers.add(decomposed_modifier)

        return self

    @abstractmethod
    def _validate_modifier(self, modifier: _ExtendsStringModifier) -> None: ...

    def _apply_modifiers(self, s: str) -> str:
        for modifier in self._decomposed_modifiers:
            s = self._apply_modifier(s, modifier)

        return s

    @staticmethod
    def _apply_modifier(s: str, modifier: _ExtendsDecomposedStringModifier) -> str:
        if modifier == "quoted:single":
            return f"'{s}'"
        elif modifier == "quoted:double":
            return f'"{s}"'
        elif modifier == "quoted:code":
            return f"`{s}`"

        return s

    @abstractmethod
    def __copy__(self) -> _StringModificationBehaviourSubtype: ...


class String(_StringModificationBehaviour["String", StringModifier, _DecomposedStringModifier]):
    _MODIFIER_ALREADY_USED_ERROR = StringModifierAlreadyUsed

    _s: str
    _config: Config
    _decomposed_modifiers: set[_DecomposedStringModifier]

    def __init__(self, s: str, config: Config | None = None) -> None:
        self._s = s
        self._config = config or Config()
        self._decomposed_modifiers = set()

    def _validate_modifier(self, modifier: _ExtendsStringModifier) -> None:
        if not is_string_modifier(modifier):
            raise InvalidSequenceModifier(modifier)

    def __str__(self) -> str:
        return self._apply_modifiers(self._s)

    def __copy__(self) -> "String":
        copy_ = type(self)(self._s, self._config)
        copy_._decomposed_modifiers = {modifier for modifier in self._decomposed_modifiers}

        return copy_


class Name(String):
    _name: str

    def __init__(self, named: _Named, config: Config | None = None) -> None:
        self._name = named.__name__

        super().__init__(self._name, config)

    def __copy__(self) -> "Name":
        named_cls = type("Named", (), {"__name__": self._name})

        copy_ = type(self)(cast(_Named, named_cls()), self._config)
        copy_._decomposed_modifiers = {modifier for modifier in self._decomposed_modifiers}

        return copy_


class TypeName(String):
    _name: str

    def __init__(self, instance: Any, config: Config | None = None) -> None:
        type_ = type(instance)
        self._name = type_.__name__

        if not isinstance(type_, _Named):
            raise UnexpectedType(
                f"Type `{self._name}` "
                f"of instance '{instance}' does have `__name__` attribute."
            )

        super().__init__(type_.__name__, config)

    def __copy__(self) -> "TypeName":
        class Named:
            __name__ = self._name

        copy_ = type(self)(Named(), self._config)
        copy_._decomposed_modifiers = {modifier for modifier in self._decomposed_modifiers}

        return copy_


class Sequence(_StringModificationBehaviour["Sequence", SequenceModifier, _DecomposedSequenceModifier]):
    _MODIFIER_ALREADY_USED_ERROR = SequenceModifierAlreadyUsed

    _lst: list[WithStringModifications]
    _config: Config
    _shorten_if_longer_than: int | None
    _decomposed_modifiers: set[_DecomposedSequenceModifier]

    def __init__(self, it: Iterable[str | WithStringModifications], config: Config | None = None) -> None:
        self._config = config or Config()
        self._lst = [human_readable(item) for item in it]
        self._shorten_if_longer_than = self._config.default_shorten_sequence_if_longer_than
        self._decomposed_modifiers = set()

    if TYPE_CHECKING:
        def modified(
                self,
                modifier: "SequenceModifier"
        ) -> "Sequence": ...

        def quoted(self, style: QuoteStyle | None = None) -> "Sequence": ...

        def double_quoted(self) -> "Sequence": ...

        def single_quoted(self) -> "Sequence": ...

        def code(self) -> "Sequence": ...

    def items_quoted(self, style: QuoteStyle | None = None) -> "Sequence":
        self._lst = [item.quoted(style) for item in self._lst]

        return self

    def items_single_quoted(self) -> "Sequence":
        self._lst = [item.single_quoted() for item in self._lst]

        return self

    def items_double_quoted(self) -> "Sequence":
        self._lst = [item.double_quoted() for item in self._lst]

        return self

    def items_code(self) -> "Sequence":
        self._lst = [item.code() for item in self._lst]

        return self

    def separated(self, delimiter: Literal[",", "|"]) -> "Sequence":
        return self.modified(cast(SequenceModifier, f"delimiter:{delimiter}"))

    def comma_separated(self) -> "Sequence":
        return self.separated(",")

    def pipe_separated(self) -> "Sequence":
        return self.separated("|")

    def with_conjunction(self, conjunction: Literal["and", "or", "and/or"]) -> "Sequence":
        return self.modified(cast(SequenceModifier, f"conjunction:{conjunction}"))

    def anded(self) -> "Sequence":
        return self.with_conjunction("and")

    def ored(self) -> "Sequence":
        return self.with_conjunction("or")

    def and_ored(self) -> "Sequence":
        return self.with_conjunction("and/or")

    def sorted(self) -> "Sequence":
        copy_ = copy(self)
        copy_._lst.sort()

        return copy_

    def appended(self, item: str | WithStringModifications) -> "Sequence":
        copy_ = copy(self)
        copy_._lst.append(human_readable(item))

        return copy_

    def extended(self, it: Iterable) -> "Sequence":
        copy_ = copy(self)
        copy_._lst.extend([human_readable(item) for item in it])

        return copy_

    def shorten_if_longer_than(self, length: int) -> "Sequence":
        self._shorten_if_longer_than = length

        return self

    def _validate_modifier(self, modifier: SequenceModifier) -> None:
        if not is_sequence_modifier(modifier):
            raise InvalidSequenceModifier(modifier)

    def _apply_lst_modifiers(
            self,
            lst: list[str],
            modifiers: set[_DecomposedSequenceModifier]
    ) -> list[str]:
        lst = lst[:]

        lst = self._apply_shortening(lst)
        lst = self._apply_delimiters(lst, modifiers)
        lst = self._apply_conjunctions(lst, modifiers)

        return lst

    def _apply_shortening(
            self,
            lst: list[str],
    ) -> list[str]:
        if self._shorten_if_longer_than is None or len(lst) <= self._shorten_if_longer_than:
            return lst

        items_from_start_count = int(math.ceil(self._shorten_if_longer_than / 2))
        items_from_end_count = self._shorten_if_longer_than - items_from_start_count

        return lst[:items_from_start_count] + ["..."] + lst[-items_from_end_count:]

    def _apply_delimiters(
            self,
            lst: list[str],
            modifiers: set[_DecomposedSequenceModifier]
    ) -> list[str]:
        skip_delimiters_after_items_at_indices = {len(lst) - 2} if "conjunction" in modifiers else set()

        if "delimiter:," in modifiers:
            lst = self._apply_delimiter(lst, ", ", skip_delimiters_after_items_at_indices)
        elif "delimiter:|" in modifiers:
            lst = self._apply_delimiter(lst, " | ", skip_delimiters_after_items_at_indices)
        elif self._config.default_sequence_delimiter == ",":
            lst = self._apply_delimiter(lst, ", ", skip_delimiters_after_items_at_indices)
        elif self._config.default_sequence_delimiter == "|":
            lst = self._apply_delimiter(lst, " | ", skip_delimiters_after_items_at_indices)

        return lst

    def _apply_conjunctions(
            self,
            lst: list[str],
            modifiers: set[_DecomposedSequenceModifier]
    ) -> list[str]:
        if "conjunction:and" in modifiers:
            lst = self._apply_conjunction(lst, "and")
        elif "conjunction:or" in modifiers:
            lst = self._apply_conjunction(lst, "or")
        elif "conjunction:and/or" in modifiers:
            lst = self._apply_conjunction(lst, "and/or")
        elif self._config.default_sequence_delimiter == "and":
            lst = self._apply_conjunction(lst, "and")
        elif self._config.default_sequence_delimiter == "or":
            lst = self._apply_conjunction(lst, "or")
        elif self._config.default_sequence_delimiter == "and/or":
            lst = self._apply_conjunction(lst, "and/or")

        return lst

    @staticmethod
    def _apply_delimiter(
            lst: list[str],
            delimiter: str,
            skip_delimiters_after_items_at_indices: set[int]
    ) -> list[str]:
        if len(lst) == 0:
            return lst
        else:
            new_lst: list[str] = []
            for i, item in enumerate(lst[:-1]):
                if i in skip_delimiters_after_items_at_indices:
                    new_lst.append(item)
                else:
                    new_lst.append(item)
                    new_lst.append(delimiter)
            new_lst.append(lst[-1])

            return new_lst

    @staticmethod
    def _apply_conjunction(
            lst: list[str],
            conjunction: str
    ) -> list[str]:
        if len(lst) < 2:
            return lst[:]
        else:
            return lst[:-1] + [f" {conjunction} ", lst[-1]]

    def __str__(self) -> str:
        str_lst = self._apply_lst_modifiers(
            [str(item) for item in self._lst],
            self._decomposed_modifiers
        )

        return super()._apply_modifiers("".join(str_lst))

    def __copy__(self) -> "Sequence":
        copy_ = type(self)(
            [copy(item) for item in self._lst],
            self._config
        )
        copy_._decomposed_modifiers = {modifier for modifier in self._decomposed_modifiers}

        return copy_


@runtime_checkable
class _WithBasesAndName(_Named, Protocol):

    __bases__: tuple

    __name__: str


@overload
def human_readable(obj: str, config: Config | None = None) -> String: ...


@overload
def human_readable(obj: Iterable, config: Config | None = None) -> Sequence: ...


@overload
def human_readable(obj: Type[bool | int | float | str] | _WithBasesAndName, config: Config | None = None) -> Name: ...


@overload
def human_readable(obj: Any, config: Config | None = None) -> String: ...


def human_readable(obj, config: Config | None = None):
    if type(obj) is str:
        return String(obj, config)
    elif isinstance(obj, Iterable):
        return Sequence(obj, config)
    elif _is_primitive_type(obj) or isinstance(obj, _WithBasesAndName):
        return Name(obj, config)

    return String(str(obj), config)


def _is_primitive_type(obj: Any) -> bool:
    return obj in {bool, int, float, str}
