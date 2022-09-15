import dataclasses
from dataclasses import dataclass
from pathlib import Path

from . import cache
from . import validate


@dataclass(frozen=True)
class ExpectedDirectoryContents:
    files: set[str] = dataclasses.field(default_factory=set)
    dirs: set[str] = dataclasses.field(default_factory=set)


# We don't want to make indicators too strict,
# to avoid changes breaking path discovery
_DIR_CONTENTS_INDICATING_PROJECT_ROOT = ExpectedDirectoryContents(
    dirs={".git"}
)
_DIR_CONTENTS_INDICATING_BACKEND_DIR = ExpectedDirectoryContents(
    files={"requirements.txt"}
)


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


@cache.return_singleton
def find_project_root() -> Path:
    """
    Returns the root of the git repository.
    """
    return find_first_parent_with_contents(
        abs_from_str(__file__),
        _DIR_CONTENTS_INDICATING_PROJECT_ROOT
    )


@cache.return_singleton
def find_backend() -> Path:
    """
    Returns the directory containing the python backend source code.
    """
    return find_first_parent_with_contents(
        abs_from_str(__file__),
        _DIR_CONTENTS_INDICATING_BACKEND_DIR
    )


@cache.return_singleton
def find_logs() -> Path:
    return find_backend() / "logs"
