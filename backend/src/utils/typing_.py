import types
import typing
from collections.abc import Iterable


def extract_strings_from_type(type_: typing.Any) -> Iterable[str]:
    if (origin_type := typing.get_origin(type_)) is typing.Literal:
        for type_arg in typing.get_args(type_):
            if type(type_arg) is not str:
                raise TypeError(
                    f"Cannot extract strings "
                    f"from Literal with non-string argument '{type_arg}'"
                )

            yield type_arg
    elif origin_type is types.UnionType:
        for arg_type in typing.get_args(type_):
            yield from extract_strings_from_type(arg_type)
    else:
        raise TypeError(
            f"Can only extract strings from Literal or Union types, not '{type_}'"
        )
