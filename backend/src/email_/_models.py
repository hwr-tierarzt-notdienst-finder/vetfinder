from __future__ import annotations

from typing import ClassVar, Any, Type

from pydantic import BaseModel
from pydantic.config import BaseConfig

# Populated by '__init_subclass__' methods (see below)
_type_to_header_segment: dict[str, Type[HeaderSegment]] = {}
_type_to_body_segment: dict[str, Type[BodySegment]] = {}


def get_header_segment_by_type(type_: str) -> Type[HeaderSegment]:
    return _type_to_header_segment[type_]


def get_body_segment_by_type(type_: str) -> Type[BodySegment]:
    return _type_to_body_segment[type_]


class Segment(BaseModel):
    TYPE: ClassVar[str]

    class Config(BaseConfig):
        orm_mode = True


class HeaderSegment(Segment):

    def __init_subclass__(cls, **kwargs: Any) -> None:
        _type_to_header_segment[cls.TYPE] = cls


class BodySegment(Segment):

    def __init_subclass__(cls, **kwargs: Any) -> None:
        _type_to_body_segment[cls.TYPE] = cls


class SubjectSegment(HeaderSegment):
    TYPE = "subject"

    text: str


class TextSegment(BodySegment):
    TYPE = "text"

    text: str


class PrimaryCTALinkButton(BodySegment):
    TYPE = "primary_cta_link_button"

    text: str
    url: str
