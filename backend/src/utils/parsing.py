import string
from collections.abc import Iterator, Container, Iterable
from typing import Callable, NoReturn


class Error(ValueError):
    pass


class LR1Iter(Iterator):
    _char_iter: Iterator[str]
    _has_ended: bool
    _next_char: str | None

    def __init__(self, s: Iterable[str]) -> None:
        self._char_iter = iter(s)
        self._has_ended = False
        self._set_next_char()

    def while_char_matches(
            self,
            match_char: Callable[[str], bool]
    ) -> Iterator[str]:
        while self.look_ahead() is not None and match_char(self.look_ahead()):
            yield next(self)

    def until_char_matches(
            self,
            match_char: Callable[[str], bool]
    ) -> Iterator[str]:
        while not match_char(self.look_ahead()):
            yield next(self)

    def skip_while_matches(
            self,
            match_char: Callable[[str], bool]
    ) -> None:
        for _ in self.while_char_matches(match_char):
            pass

    def skip_until_matches(
            self,
            match_char: Callable[[str], bool]
    ) -> None:
        for _ in self.until_char_matches(match_char):
            pass

    def skip_chars(
            self,
            chars: Container[str]
    ) -> None:
        def is_chars_to_skip(char: str) -> bool:
            return char in chars

        self.skip_while_matches(is_chars_to_skip)

    def skip_whitespace(
            self
    ) -> None:
        self.skip_chars(string.whitespace)

    def look_ahead(self) -> str | None:
        return self._next_char

    def advance(self) -> str:
        current_char = self._next_char

        if current_char is None:
            self._has_ended = True

            raise StopIteration

        self._set_next_char()

        return current_char

    def advance_while_matching_or_fail(
            self,
            s: Iterable[str]
    ) -> None | NoReturn:
        other = type(self)(s)

        while other.look_ahead() is not None:
            try:
                if self.look_ahead() != other.look_ahead():
                    raise Error(
                        f"Parsed characters do not match '{s}'"
                    )

                self.advance()
                other.advance()
            except StopIteration:
                raise Error(
                    f"Parsed string iterable ended before '{s}' could be fully matched"
                )

    def __next__(self) -> str:
        return self.advance()

    def __bool__(self) -> bool:
        return not self._has_ended

    def _set_next_char(self) -> None:
        try:
            self._next_char = next(self._char_iter)
        except StopIteration:
            self._next_char = None
