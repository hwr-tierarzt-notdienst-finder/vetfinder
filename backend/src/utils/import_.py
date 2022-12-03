from pathlib import Path
from types import ModuleType
from typing import Iterable
from importlib import import_module


def iter_submodules(
        parent_module: ModuleType,
        ignore_modules_with_prefixes: Iterable[str] | None = None
) -> Iterable[ModuleType]:
    if ignore_modules_with_prefixes is None:
        ignore_modules_with_prefixes = {"_", "__"}

    parent_path = Path(parent_module.__path__[0]).resolve()

    for child_path in parent_path.iterdir():
        if any(
                child_path.name.startswith(prefix)
                for prefix in ignore_modules_with_prefixes
        ):
            continue

        yield import_module(
            f".{child_path.stem}",
            parent_module.__name__,
        )


