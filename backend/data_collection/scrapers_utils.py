import string

import requests
from typing import Callable, Literal, Iterable

from bs4 import BeautifulSoup


def _fetch_html_from_url(url: str) -> str:
    response = requests.get(url)

    return response.text


def get_soup_from_url(
        url: str,
        *,
        parser: Literal["lxml", "html5lib"] = "lxml",
        fetch_html: Callable[[str], str] = _fetch_html_from_url,
        encoding: str | None = None,
) -> BeautifulSoup:
    return BeautifulSoup(fetch_html(url), parser, from_encoding=encoding)


class AggregateNormalizer:
    _DEFAULT_WHITESPACE = {
        " ",
        "\t",
        "\n",
        "\r",
        "\v",
        "\f",
        "\xa0"  # &nbsp;
    }

    _normalizers: list[Callable[[str], str]]
    _whitespace: set[str]

    def __init__(
            self,
            normalizers: list[Callable[[str], str]] | None = None,
            *,
            whitespace: set[str] | None = None
    ) -> None:
        self._normalizers = normalizers or []
        self._whitespace = whitespace or self._DEFAULT_WHITESPACE

    def add_normalizer(
            self,
            normalizer: Callable[[str], str]
    ) -> "AggregateNormalizer":
        return type(self)(
            self._normalizers[:] + [normalizer],
            whitespace=set(self._whitespace),
        )

    def replace(self, target: str | set[str], replacement: str) -> "AggregateNormalizer":
        if type(target) is str:
            targets = {target}
        elif hasattr(target, "__iter__"):
            targets = set(target)
        else:
            raise TypeError(
                "Expected argument 'target' to be a string or an iterable yielding strings"
            )

        def normalizer(text: str) -> str:
            for target_ in targets:
                text = text.replace(target_, replacement)

            return text

        return self.add_normalizer(normalizer)

    def unify_whitespace(self, to: str = " ") -> "AggregateNormalizer":
        return self.replace(self._whitespace, to)

    def remove_prefix(
            self, prefix: str | Iterable[str],
            n: int | None = None
    ) -> "AggregateNormalizer":
        if type(prefix) is str:
            prefixes = {prefix}
        elif hasattr(prefix, "__iter__"):
            prefixes = set(prefix)
        else:
            raise TypeError(
                "Expected argument 'prefix' to be a string or an iterable yielding strings"
            )

        def normalizer(text: str) -> str:
            i = 0
            while True:
                if n is not None and i >= n:
                    return text

                for prefix_ in prefixes:
                    if text.startswith(prefix_):
                        text = text.removeprefix(prefix_)
                        break
                else:
                    break

                i += 1

            return text

        return self.add_normalizer(normalizer)

    def remove_leading_whitespace(self, n: int | None = None) -> "AggregateNormalizer":
        return self.remove_prefix(self._whitespace, n)

    def remove_suffix(
            self, suffix: str | Iterable[str],
            n: int | None = None
    ) -> "AggregateNormalizer":
        if type(suffix) is str:
            suffixes = {suffix}
        elif hasattr(suffix, "__iter__"):
            suffixes = set(suffix)
        else:
            raise TypeError(
                "Expected argument 'suffix' to be a string or an iterable yielding strings"
            )

        def normalizer(text: str) -> str:
            i = 0
            while True:
                if n is not None and i >= n:
                    return text

                for suffix_ in suffixes:
                    if text.endswith(suffix_):
                        text = text.removesuffix(suffix_)
                        break
                else:
                    break

                i += 1

            return text

        return self.add_normalizer(normalizer)

    def remove_tailing_whitespace(self, n: int | None = None) -> "AggregateNormalizer":
        return self.remove_suffix(self._whitespace, n)

    def remove_enclosing(
            self,
            enclosure: str | Iterable[str],
            *,
            n_start: int | None = None,
            n_end: int | None = None,
    ) -> "AggregateNormalizer":
        return (
            self.remove_prefix(enclosure, n_start)
            .remove_suffix(enclosure, n_end)
        )

    def remove_enclosing_whitespace(
            self,
            *,
            n_start: int | None = None,
            n_end: int | None = None,
    ):
        return self.remove_enclosing(
            self._whitespace,
            n_start=n_start,
            n_end=n_end
        )

    def __call__(self, text: str) -> str:
        for normalize in self._normalizers:
            text = normalize(text)

        return text
