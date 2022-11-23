import dataclasses
from dataclasses import dataclass
from pathlib import Path

from . import validate


@dataclass(frozen=True)
class ExpectedDirectoryContents:
    files: set[str] = dataclasses.field(default_factory=set)
    dirs: set[str] = dataclasses.field(default_factory=set)


def abs_from_str(s: str) -> Path:
    return Path(s).resolve()


def from_(path: str | Path) -> Path:
    if type(path) is str:
        return abs_from_str(path)

    return path.resolve()


def dir_(path: Path) -> Path:
    return validate.path_is_dir(path)


def dir_from(path: str | Path) -> Path:
    return dir_(from_(path))


def find_first_parent_with_contents(
        start_path: Path,
        contents: ExpectedDirectoryContents
) -> Path:
    parent: Path | None = None
    for parent in start_path.resolve().parents:
        parent_file_contents_names: set[str] = set()
        parent_dir_contents_names: set[str] = set()

        for item in parent.iterdir():
            if item.is_file():
                parent_file_contents_names.add(item.name)
            elif item.is_dir():
                parent_dir_contents_names.add(item.name)

        if (
                contents.files.issubset(parent_file_contents_names)
                and contents.dirs.issubset(parent_dir_contents_names)
        ):
            break

    if parent is None:
        raise ValueError(
            f"Could not find parent of '{start_path}' with contents '{contents}'"
        )

    return parent
