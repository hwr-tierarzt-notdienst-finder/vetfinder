import string
from collections import deque
from collections.abc import Callable
import dataclasses
from dataclasses import dataclass
from functools import wraps
from typing import ParamSpec, Protocol, TypeVar, Any, cast

_P = ParamSpec("_P")
_R = TypeVar("_R")


def _access_path_default(
        obj: Any,
        path: tuple[str | int, ...]
) -> Any:
    if path == ():
        return obj

    key, *child_path = path
    child_path = tuple(child_path)

    if type(key) is int:
        child_obj = obj[key]
    else:
        try:
            child_obj = getattr(obj, key)
        except AttributeError as err:
            try:
                child_obj = obj[key]
            except KeyError:
                raise err

    return _access_path_default(child_obj, child_path)


@dataclass(frozen=True)
class Config:
    placeholder_start: str = "{"
    placeholder_end: str = "}"
    escape: str = "\\"
    path_sep: str = "."
    rel_path_start: str = "."
    root_path_start: str = ""
    error_underline_char: str = "^"
    access_path: Callable[[tuple[str | int, ...]], Any] = _access_path_default


class _WithConfigKwargs(Protocol[_P, _R]):

    def __call__(
            self,
            *args: _P.args,
            config: Config | None = None,
            placeholder_start: str | None = None,
            placeholder_end: str | None = None,
            escape: str | None = None,
            path_sep: str | None = None,
            rel_path_start: str | None = None,
            root_path_start: str | None = None,
            **kwargs: _P.kwargs
    ) -> _R:
        ...


class _WithSingleConfigKwarg(Protocol[_P, _R]):

    def __call__(
            self,
            *args: _P.args,
            config: Config,
            **kwargs: _P.kwargs
    ) -> _R:
        ...


def _use_config_kwargs(wrapped:  _WithSingleConfigKwarg[_P, _R]) -> _WithConfigKwargs[_P, _R]:
    config_kwarg_names = {field.name for field in dataclasses.fields(Config)}

    @wraps(wrapped)
    def wrapper(*args: _P.args, **kwargs: Any) -> _R:
        config_kwargs: dict[str, Any] = {}
        non_config_kwargs: dict[str, Any] = {}

        for name, value in kwargs.items():
            if name in config_kwarg_names and value is not None:
                config_kwargs[name] = value
            else:
                non_config_kwargs[name] = value

        if (config := non_config_kwargs.get("config", None)) is not None:
            if config_kwargs:
                raise ValueError(
                    f"Callable '{wrapped.__name__}' cannot pass any configuration kwargs "
                    f"if 'config' is passed"
                )

            del non_config_kwargs["config"]
        else:
            config = Config(**config_kwargs)

        return wrapped(*args, config=config, **non_config_kwargs)

    return cast(_WithConfigKwargs[_P, _R], wrapper)


@_use_config_kwargs
def replace(
        text: str,
        obj: dict,
        current_path: str | None = None,
        *,
        config: Config
) -> str:
    if current_path is None:
        current_path = config.root_path_start

    current_chars: deque[str] = deque(
        maxlen=max(len(config.placeholder_start), len(config.placeholder_end)) + 2 * len(config.escape)
    )
    is_in_placeholder = False
    placeholder_start_index = 0
    placeholder_chars: list[str] = []
    out_chars: list[str] = []

    def create_error(start_index: int, end_index: int, msg: str) -> Exception:
        error_lines: list[str] = [""]
        in_violating_lines = False
        line_break_indices = [0] + [char_index + 1 for char_index, char in enumerate(text) if char == "\n"] + [len(text)]
        for line_index, (line_start_index, line_end_index) in enumerate(
                zip(line_break_indices[:-1], line_break_indices[1:])
        ):
            if in_violating_lines:
                if end_index <= line_end_index:
                    break
            elif start_index < line_end_index:
                in_violating_lines = True
            else:
                continue

            line = text[line_start_index:line_end_index - 1]
            on_line_start_index = max(start_index, line_start_index) - line_start_index
            on_line_end_index = min(end_index, line_end_index - 1) - line_start_index
            prefix = f"{line_index + 1}:{on_line_start_index + 1}-{on_line_end_index + 1} | "
            error_lines.append(
                f"{prefix}{line}"
            )
            error_lines.append(
                " " * (len(prefix) + on_line_start_index)
                + config.error_underline_char * ((on_line_end_index - on_line_start_index) or 1)
                + " " * (line_end_index - on_line_end_index)
            )

        error_lines.append(msg)

        return ValueError("\n".join(error_lines))

    def control_sequence_was_escaped(
            control_seq_name: str,
            current_char_index: int,
            control_seq: str
    ) -> bool:
        current_chars_str = "".join(current_chars.copy())

        if current_chars_str.endswith(f"{config.escape}{config.escape}{control_seq}"):
            return False
        elif current_chars_str.endswith(f"{config.escape}{control_seq}"):
            return True
        elif current_chars_str.endswith(control_seq):
            return False

        raise create_error(
            current_char_index, current_char_index + 1,
            f"Expected {control_seq_name} '{control_seq}' control sequence"
        )

    def try_enter_placeholder(current_char_index: int) -> bool:
        nonlocal out_chars
        nonlocal is_in_placeholder
        nonlocal placeholder_start_index

        placeholder_start_index = current_char_index + 1

        if control_sequence_was_escaped(
            "placeholder start",
            current_char_index,
            config.placeholder_start
        ):
            escape_end_index = -len(config.placeholder_start) + 1 or len(out_chars)
            escape_start_index = escape_end_index - len(config.escape)
            out_chars = out_chars[:escape_start_index] + out_chars[escape_end_index:]
            return False

        is_in_placeholder = True
        placeholder_start_index = current_char_index + 1

        return True

    def try_exit_placeholder(current_char_index: int) -> bool:
        nonlocal placeholder_chars
        nonlocal is_in_placeholder

        if control_sequence_was_escaped(
            "placeholder end",
            current_char_index,
            config.placeholder_end
        ):
            escape_end_index = -len(config.placeholder_end) + 1 or len(placeholder_chars)
            escape_start_index = escape_end_index - len(config.escape)
            placeholder_chars = placeholder_chars[:escape_start_index] + placeholder_chars[escape_end_index:]
            return False

        path_str = "".join(placeholder_chars).removesuffix(config.placeholder_end[:-1]).strip()

        if config.root_path_start:
            if path_str.startswith(config.root_path_start):
                is_relative_path = False
            else:
                is_relative_path = True
        elif config.rel_path_start:
            if path_str.startswith(config.rel_path_start):
                is_relative_path = True
            else:
                is_relative_path = False
        else:
            is_relative_path = True

        if is_relative_path:
            path_str = f"{current_path}{config.path_sep}{path_str.removeprefix(config.rel_path_start)}"

        path = _path_from_str(path_str, config)

        try:
            value = str(config.access_path(obj, path))
        except (AttributeError, KeyError, IndexError) as err:
            raise create_error(
                placeholder_start_index,
                current_char_index,
                f"Could not access path '{path_str}' "
                f"on object '{obj}' with error: {err}"
            ) from err

        out_chars.append(value)
        placeholder_chars.clear()
        is_in_placeholder = False

        return True

    control_sequence_end_chars = {config.placeholder_start[-1], config.placeholder_end[-1]}

    char_index = 0
    for char_index, char in enumerate(text):
        current_chars.append(char)

        if char in control_sequence_end_chars:
            current_chars_str = "".join(current_chars.copy())

            if is_in_placeholder:
                if current_chars_str.endswith(config.placeholder_end):
                    if try_exit_placeholder(char_index):
                        continue
            else:
                if current_chars_str.endswith(config.placeholder_start):
                    if try_enter_placeholder(char_index):
                        for _ in range(len(config.placeholder_start) - 1):
                            out_chars.pop()
                        continue

        if is_in_placeholder:
            placeholder_chars.append(char)
        else:
            out_chars.append(char)

    if is_in_placeholder:
        try_exit_placeholder(char_index - 1)

    return "".join(out_chars)


def _path_from_str(s: str, config: Config) -> tuple[str | int, ...]:
    s = "".join(char for char in s if char not in string.whitespace)

    return tuple(
        int(segment) if segment.isdigit() else segment
        for segment in s.split(config.path_sep)
        if segment != ""
    )
