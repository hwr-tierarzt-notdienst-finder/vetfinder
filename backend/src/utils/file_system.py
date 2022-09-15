import os
from contextlib import contextmanager
from pathlib import Path
from shutil import rmtree
from typing import TextIO, TypedDict, Literal, Iterable, TypeVar, NoReturn, cast

from .. import types_
from .human_readable import human_readable
from . import string

_T = TypeVar("_T")


class _DirBaseEntry(TypedDict):
    name: str


class _DirFileEntry(_DirBaseEntry):
    type: Literal["file"]
    contents: "_FileContents"


class _DirDirEntry(_DirBaseEntry):
    type: Literal["file"]
    contents: "_DirContents"


_DirEntry = _DirFileEntry | _DirDirEntry
_FileContents = str | Iterable[str] | None
_DirContents = Iterable[_DirEntry] | None


class _MatchDirBaseEntry(TypedDict):
    match_name: types_.string.Matcher


class _MatchDirFileEntry(_MatchDirBaseEntry):
    type: Literal["file"]
    match_contents: "_MatchFileContents"


class _MatchDirDirEntry(_MatchDirBaseEntry):
    type: Literal["dir"]
    match_contents: "_MatchDirContents"


_MatchDirEntry = _MatchDirFileEntry | _MatchDirDirEntry
_MatchFileContents = types_.string.Matcher | Iterable[types_.string.Matcher]
_MatchDirContents = Iterable[_MatchDirEntry]


@contextmanager
def temp_file(
        path: str | Path,
        contents: _FileContents = None,
        *,
        remove_on_failure: bool = True,
) -> Iterable[TextIO]:
    path = Path(path).resolve()

    try:
        yield create_file(
            path,
            contents,
            remove_on_failure=remove_on_failure,
        )
    except Exception as err:
        if remove_on_failure:
            path.unlink()

        raise err
    else:
        path.unlink()


@contextmanager
def temp_dir(
        path: str | Path,
        contents: _DirContents = None,
        *,
        parents: bool = False,
        exist_ok: bool = False,
        remove_on_failure: bool = True,
) -> Path:
    path = Path(path).resolve()

    try:
        yield create_dir(
            path,
            contents,
            parents=parents,
            exist_ok=exist_ok,
            remove_on_failure=remove_on_failure,
        )
    except Exception as err:
        if remove_on_failure:
            rmtree(path)

        raise err
    else:
        rmtree(path)


def matches_contents(
        path: str | Path,
        expected_contents: _MatchDirEntry,
) -> bool:
    try:
        matching_contents(path, expected_contents)
    except ValueError:
        return False

    return True


def matching_file_contents(
        path: str | Path,
        expected_contents: _MatchFileContents,
) -> Path | NoReturn:
    matching_contents(
        path,
        {
            "type": "file",
            "match_name": path.name,
            "match_contents": expected_contents,
        }
    )


def matching_dir_contents(
        path: str | Path,
        expected_contents: _MatchDirContents,
) -> Path | NoReturn:
    matching_contents(
        path,
        {
            "type": "dir",
            "match_name": path.name,
            "match_contents": expected_contents,
        }
    )


def matching_contents(
        path: str | Path,
        expected_contents: _MatchDirEntry,
) -> Path | NoReturn:
    path = Path(path).resolve()

    name_matcher = expected_contents["match_name"]

    if not string.matches(path.name, name_matcher):
        raise ValueError(
            f"Path '{path}' name '{path.name}' does not match '{name_matcher}'"
        )

    expected_type = expected_contents["type"]

    if path.is_file():
        if expected_type != "file":
            raise ValueError(
                f"Path '{path}' was expected to be a file"
            )

        contents_matcher = expected_contents["match_contents"]

        with open(path) as f:
            err: ValueError | None = None

            try:
                if not string.matches(f.read(), contents_matcher):
                    err = ValueError(
                        f"Contents of file '{path}' does not match '{contents_matcher}'"
                    )
            except ValueError as e:
                err = e

            if err is not None:
                f.seek(0)
                lines = iter(f.readlines())
                line_matchers = iter(contents_matcher)

                line_num = 1
                while True:
                    try:
                        line = next(lines).removesuffix(os.linesep)
                    except StopIteration:
                        break

                    try:
                        line_matcher = next(line_matchers)
                    except StopIteration as err:
                        raise ValueError(
                            "Contents matchers for lines must yield at least as many items as number of lines. "
                            f"File '{path}' has at least {line_num} lines"
                        ) from err

                    if not string.matches(line, line_matcher):
                        raise ValueError(
                            f"Line {line_num} '{line}' of file '{path}' does not match '{line_matcher}'"
                        )

                    line_num += 1

                err = None

            if err is not None:
                raise err

        return path

    elif path.is_dir():
        if expected_type != "dir":
            raise ValueError(
                f"Path '{path}' was expected to be a directory"
            )

        children = list(path.iterdir())
        matched_children = set()
        child_to_first_match_error: dict[Path, ValueError] = {}

        for child_expected_contents in cast(_MatchDirContents, expected_contents["match_contents"]):
            name_matcher = child_expected_contents["match_name"]

            # Narrow search space
            children_with_matching_name = {
                child for child in children
                if string.matches(child.name, name_matcher)
            }

            for child in children_with_matching_name:
                try:
                    matching_contents(child, child_expected_contents)
                except ValueError as err:
                    if child not in child_to_first_match_error:
                        child_to_first_match_error[child] = err
                else:
                    matched_children.add(child)

        unmatched_children = set(children) - matched_children
        if len(unmatched_children) > 0:
            sorted_unmatched_children_names = sorted(
                [child.name for child in unmatched_children]
            )

            child_errors_substr = "\n".join(
                f"{child.name}: {err}"
                for child, err in child_to_first_match_error.items()
            )

            raise ValueError(
                f"Children {human_readable(sorted_unmatched_children_names).quoted().anded()} "
                f"of directory '{path}' did not match expected contents, with errors:\n\n"
                f"{child_errors_substr}"
            )

    else:
        raise ValueError(
            f"Unexpected path type for '{path}'. Expected file or directory"
        )


def read_contents(
        path: str | Path,
        *,
        file_contents_as: str | list = str,
        empty_file_as_none: bool = False,
        empty_dir_as_none: bool = False,
) -> _DirEntry:
    path = Path(path).resolve()

    type_: Literal["file", "dir"]
    if path.is_file():
        type_ = "file"
    elif path.is_dir():
        type_ = "dir"
    else:
        raise ValueError(
            f"Cannot read directory entry '{path}' which isn't a file or directory"
        )

    return {
        "type": type_,
        "name": path.name,
        "contents": (
            read_file_contents(
                path,
                file_contents_as=file_contents_as,
                empty_file_as_none=empty_file_as_none,
            ) if type_ == "file"
            else read_dir_contents(
                path,
                file_contents_as=file_contents_as,
                empty_file_as_none=empty_file_as_none,
                empty_dir_as_none=empty_dir_as_none,
            )
        ),
    }


def read_file_contents(
        path: str | Path,
        *,
        file_contents_as: str | list = str,
        empty_file_as_none: bool = False,
) -> _FileContents:
    path = Path(path).resolve()

    with open(path, "r") as f:
        if file_contents_as is str:
            contents = f.read()
            if contents == "" and empty_file_as_none:
                return None
            return contents
        elif file_contents_as is list:
            lines = f.readlines()
            if lines == [] and empty_file_as_none:
                return None
            return lines
        else:
            raise ValueError(
                "Argument 'file_contents_as' must be 'str' or 'list'"
            )


def read_dir_contents(
        path: str | Path,
        *,
        file_contents_as: str | list = str,
        empty_file_as_none: bool = False,
        empty_dir_as_none: bool = False,
) -> _DirContents:
    path = Path(path).resolve()

    contents: list[_DirEntry] = []
    for child_path in path.iterdir():
        contents.append(
            read_contents(
                child_path,
                file_contents_as=file_contents_as,
                empty_file_as_none=empty_file_as_none,
                empty_dir_as_none=empty_dir_as_none,
            )
        )

    if contents == [] and empty_file_as_none:
        return None

    return contents


def create_file(
        path: Path,
        contents: _FileContents = None,
        *,
        remove_on_failure: bool = True,
) -> TextIO:
    try:
        with open(path, "x") as f:
            if contents is not None:
                if type(contents) is str:
                    f.write(contents)
                elif hasattr(contents, "__iter__"):
                    f.write(os.linesep.join(contents))
                else:
                    raise ValueError("Contents must be a string or list of strings")

            return f
    except Exception as err:
        if remove_on_failure:
            path.unlink()

        raise err


def create_dir(
        path: Path,
        contents: _DirContents = None,
        *,
        parents: bool = False,
        exist_ok: bool = False,
        remove_on_failure: bool = True,
) -> Path:
    path.mkdir(parents=parents, exist_ok=exist_ok)

    try:
        if contents is not None:
            for entry in contents:
                if entry["type"] == "file":
                    create_file(
                        path / entry["name"],
                        entry["contents"],
                        remove_on_failure=remove_on_failure,
                    )
                elif entry["type"] == "dir":
                    create_dir(
                        path / entry["name"],
                        entry["contents"],
                        remove_on_failure=remove_on_failure,
                    )
                else:
                    raise ValueError(
                        f"Contents entry type must be 'file' or 'dir', not '{entry['type']}'"
                    )
    except Exception as err:
        if remove_on_failure:
            rmtree(path)

        raise err

    return path
