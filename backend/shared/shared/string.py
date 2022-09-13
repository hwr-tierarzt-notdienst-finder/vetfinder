import re
from typing import NoReturn, Callable, TypeVar, cast

from .human_readable import human_readable
from .types.string import HowManyShouldMatch, Matcher

_TStr = TypeVar("_TStr", bound=str)


def matches(
        target: str,
        matcher: Matcher,
        /,
        *matchers: Matcher,
        how_many_should_match: HowManyShouldMatch = "all",
) -> bool:
    matcher = create_matcher(
        matcher,
        *matchers,
        how_many_should_match=how_many_should_match
    )

    return matcher(target)


def matching(
        target: _TStr,
        matcher: Matcher,
        /,
        *matchers: Matcher,
        how_many_should_match: HowManyShouldMatch = "all",
) -> _TStr | NoReturn:
    validator = create_match_validator(
        matcher,
        *matchers,
        how_many_should_match=how_many_should_match,
    )

    return validator(target)


def create_matcher(
        matcher: Matcher,
        *matchers: Matcher,
        how_many_should_match: HowManyShouldMatch = "all",
) -> Callable[[str], bool]:
    """
    Returns a matcher function that returns true if conditions inferred
    from the positional matcher arguments are met.

    :param how_many_should_match:
        A string describing how many the conditions inferred from
        the positional arguments need to be met for the returning
        matcher function to return true.
    """
    if len(matchers) > 0:
        matcher = (
            how_many_should_match,
            [matcher] + list(matchers)
        )

    if type(matcher) is str:

        def check(s: str) -> bool:
            return s == matcher

        return check

    elif type(matcher) is tuple:
        matcher_type = matcher[0]
        value = matcher[1]

        if matcher_type == "full":

            def check(s: str) -> bool:
                return s == value

        elif matcher_type == "start":

            def check(s: str) -> bool:
                return s.startswith(value)

        elif matcher_type == "end":

            def check(s: str) -> bool:
                return s.endswith(value)

        elif matcher_type == "regex":

            def check(s: str) -> bool:
                return re.match(re.compile(cast(str, value)), s) is not None

        elif matcher_type == "regex:full":

            def check(s: str) -> bool:
                return re.fullmatch(re.compile(cast(str, value)), s) is not None

        elif matcher_type == "regex:start":

            def check(s: str) -> bool:
                return re.match(re.compile(f"^{value}"), s) is not None

        elif matcher_type == "regex:end":

            def check(s: str) -> bool:
                return re.match(re.compile(f"{value}$"), s) is not None

        elif matcher_type == "all":
            child_checks = [
                create_matcher(child_matcher)
                for child_matcher in value
            ]

            def check(s: str) -> bool:
                return all(child_check(s) for child_check in child_checks)

        elif matcher_type == "any":
            child_checks = [
                create_matcher(child_matcher)
                for child_matcher in value
            ]

            def check(s: str) -> bool:
                return any(child_check(s) for child_check in child_checks)

        elif matcher_type == "exactly_one":
            child_checks = [
                create_matcher(child_matcher)
                for child_matcher in value
            ]

            def check(s: str) -> bool:
                count = sum(
                    1 if child_check(s) else 0
                    for child_check in child_checks
                )

                return count == 1
        else:
            raise ValueError(
                f"Unexpected matcher type '{matcher_type}' as first item in tuple"
            )

        return check

    elif isinstance(matcher, re.Pattern):

        def check(s: str) -> bool:
            return re.match(matcher, s) is not None

        return check

    elif callable(matcher):

        def check(s: str) -> bool:
            result = cast(Callable, matcher)(s)

            if type(result) is bool:
                return result

            if result == s:
                return True

            raise RuntimeError(
                "Callable matchers must return a boolean, "
                "throw a value error or return the same string that was passed to them"
            )

        return check

    raise ValueError(f"Unexpected matcher {matcher}")


def create_match_validator(
        matcher: Matcher,
        /,
        *matchers: Matcher,
        how_many_should_match: HowManyShouldMatch = "all",
) -> Callable[[_TStr], _TStr | NoReturn]:
    match_func = create_matcher(
        matcher,
        *matchers,
        how_many_should_match=how_many_should_match,
    )

    def validator(s: _TStr) -> _TStr | NoReturn:
        if match_func(s):
            return s

        if len(matchers) == 0:
            raise ValueError(
                f"String '{s}' does not match '{matcher}'"
            )

        raise ValueError(
            f"String '{s}' does not match {how_many_should_match.replace('_', ' ')} of "
            f"{human_readable([matcher] + list(matchers))}"
        )

    return validator
