import inspect
from types import ModuleType
from typing import Callable, Iterable, cast

from . import scrapers
from models import Vet


Scraper = Callable[[], Iterable[Vet]]


def collect_data() -> Iterable[Vet]:
    yield from collect_data_from_scrapers(scrapers)


def collect_data_from_scrapers(module: ModuleType) -> Iterable[Vet]:
    for scraper in collect_scrapers(module):
        yield from scraper()


def collect_scrapers(module: ModuleType) -> Iterable[Scraper]:
    for member in inspect.getmembers(module):
        if inspect.isfunction(member) and member.__name__.startswith("scrape_"):
            yield cast(Scraper, member)
