from pathlib import Path

from utils import cache
from utils import path


# We don't want to make indicators too strict,
# to avoid changes breaking path discovery
_DIR_CONTENTS_INDICATING_PROJECT_ROOT = path.ExpectedDirectoryContents(
    dirs={".git"}
)
_DIR_CONTENTS_INDICATING_BACKEND_DIR = path.ExpectedDirectoryContents(
    dirs={"src"}
)


@cache.return_singleton
def find_project_root() -> Path:
    """
    Returns the root of the git repository.
    """
    return path.find_first_parent_with_contents(
        path.abs_from_str(__file__),
        _DIR_CONTENTS_INDICATING_PROJECT_ROOT
    )


@cache.return_singleton
def find_backend() -> Path:
    """
    Returns the directory containing the python backend source code.
    """
    return path.find_first_parent_with_contents(
        path.abs_from_str(__file__),
        _DIR_CONTENTS_INDICATING_BACKEND_DIR
    )


@cache.return_singleton
def find_logs() -> Path:
    return find_backend() / "logs"


@cache.return_singleton
def find_secrets() -> Path:
    return find_backend() / "secrets"
