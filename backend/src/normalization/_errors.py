from collections.abc import Iterable


class NormalizationError(Exception):

    def __init__(self, msg: str, location: str | Iterable[str]):
        self.msg = msg
        self.locations = [location] if type(location) is str else list(location)
