from collections.abc import Callable
from functools import wraps
from pathlib import Path


def _ensure_dir(func: Callable[[], Path]) -> Callable[[], Path]:
    @wraps(func)
    def wrapper() -> Path:
        path = func()

        assert path.is_dir()

        return path

    return wrapper


_project_path: Path | None = None
@_ensure_dir
def git_root() -> Path:
    global _project_path

    could_not_find_err = RuntimeError("Could not find git root path")

    if _project_path is None:
        # Climb until we find a directory with a .git subdirectory
        path = Path(__file__).resolve()
        while True:
            parent = path.parent
            is_root = path == parent
            if is_root:
                raise could_not_find_err

            if (path / ".git").is_dir():
                _project_path = path.resolve()
                break

            path = parent

    if _project_path is None:
        raise could_not_find_err

    return _project_path


@_ensure_dir
def backend() -> Path:
    return git_root() / "backend"


@_ensure_dir
def schemas() -> Path:
    return git_root() / "schemas"
