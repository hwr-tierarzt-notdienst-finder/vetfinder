import json
from collections.abc import Callable, Iterable
from email.message import EmailMessage
from pathlib import Path
import smtplib
import textwrap
from typing import TypedDict, Any, Type, cast, Sequence

if __name__ == "__main__":
    import os
    import sys

    package_path = Path(__file__).parent
    src_path = package_path.parent

    sys.path.append(str(src_path))
    sys.path.append(str(package_path))
    __package__ = package_path.name

    os.environ["ENV"] = "dev"

import config
from utils import template
from . import _models as models


class SegmentDict(TypedDict, total=False):
    type: str


class TemplateDict(TypedDict):
    header: list[SegmentDict]
    body: list[SegmentDict]


def send_mail(
        to: str,
        template_: TemplateDict | str,
        template_fill_obj: Any,
) -> None:
    template_ = _normalize_template(template_)
    _validate_template(template_)

    header_segment_models = _convert_header_templates_to_models(
        template_["header"],
        template_fill_obj,
    )
    body_segment_models = _convert_body_templates_to_models(
        template_["body"],
        template_fill_obj
    )

    _send_mail_from_models(
        to,
        header_segment_models,
        body_segment_models,
    )


def _send_mail_from_models(
        to: str,
        header_segments: Iterable[models.HeaderSegment],
        body_segments: Iterable[models.BodySegment],
) -> None:
    header_segments = list(header_segments)
    body_segments = list(body_segments)

    config_ = config.get().email

    message = EmailMessage()

    message["Subject"] = _render_subject(header_segments)
    message["From"] = config_.sender_address
    message["To"] = to

    message.set_content(_render_plaintext_content(body_segments))
    message.add_alternative(
        _render_html_content(body_segments),
        subtype="html",
    )

    with smtplib.SMTP(config_.smtp_server_hostname, config_.smtp_server_port) as server:
        server.login(config_.smtp_server_username, config_.smtp_server_password)
        server.send_message(message)


def _render_subject(header_segments: Iterable[models.HeaderSegment]) -> str:
    subject_segment: models.SubjectSegment | None = None

    for segment in header_segments:
        if isinstance(segment, models.SubjectSegment):
            if subject_segment is not None:
                raise ValueError("Email cannot have more than one subject segment")

            subject_segment = segment

    if subject_segment is None:
        raise ValueError("Email must have subject segment")

    return subject_segment.text


def _render_plaintext_content(body_segments: Iterable[models.BodySegment]) -> str:
    segments_strings: list[str] = []

    for segment in body_segments:
        if isinstance(segment, models.TextSegment):
            segments_strings.append(
                _wrap_lines(
                    segment.text,
                    config.get().email.plaintext_line_length,
                ) + "\n"
            )
        elif isinstance(segment, models.PrimaryCTALinkButton):
            inner_button_width = max(len(segment.text), len(segment.url))
            segments_strings.append(f"+-{     '-' * inner_button_width      }-+\n")
            segments_strings.append(f"| {segment.text:^{inner_button_width}s} |\n")
            segments_strings.append(f"| { segment.url:^{inner_button_width}s} |\n")
            segments_strings.append(f"+-{     '-' * inner_button_width      }-+\n\n")
        else:
            raise TypeError(
                f"Could not render segment type '{segment.__class__.__name__}' to plaintext"
            )

    plaintext = "".join(segments_strings).strip()
    return plaintext


def _render_html_content(body_segments: Iterable[models.BodySegment]) -> str:
    css: dict[str, dict[str, str]] = {
        "body": {
            "padding": "8px !important",
            "font-family": "sans-serif",
        }
    }

    segments_html, segments_css = _render_html_body(body_segments)

    css |= segments_css

    return "\n".join([
        "<html>",
        "    <head>",
        "        <style>",
        textwrap.indent(_render_css(css), " " * 12),
        "        </style>",
        "    </head>",
        "    <body>",
        textwrap.indent(segments_html, " " * 8),
        "    </body>",
        "</html>"
    ])

def _render_css(css: dict[str, dict[str, str]]) -> str:
    return "\n\n".join(
        _render_css_selector(selector_name, properties)
        for selector_name, properties in css.items()
    )


def _render_css_selector(name: str, properties: dict[str, str]) -> str:
    return "\n".join(
        [
            name + " {"
        ] + [
            f"    {property_name}: {property_value};"
            for property_name, property_value in properties.items()
        ] + [
            "}"
        ]
    )

def _render_html_body(
        body_segments: Iterable[models.BodySegment]
) -> tuple[str, dict[str, dict[str, str]]]:
    html_segments: list[str] = []
    css_classes: dict[str, dict[str, str]] = {}

    for segment_model in body_segments:
        if isinstance(segment_model, models.TextSegment):
            html, css = _render_html_text_segment(segment_model)
        elif isinstance(segment_model, models.PrimaryCTALinkButton):
            html, css = _render_html_primary_cta_link_button(segment_model)
        else:
            raise TypeError(
                f"Could not render segment type '{segment_model.__class__.__name__}' to html"
            )

        html_segments.append(html)
        css_classes |= css

    return "\n".join(html_segments), css_classes


def _render_html_text_segment(segment: models.TextSegment) -> tuple[str, dict[str, dict[str, str]]]:
    out_lines: list[str] = []
    paragraph_lines: list[str] = []

    def is_in_paragraph() -> bool:
        return len(paragraph_lines) != 0

    def add_paragraph() -> None:
        out_lines.append("<p>")
        for i in range(len(paragraph_lines)):
            line = paragraph_lines[i]
            is_last_line = i == len(paragraph_lines) - 1
            out_lines.append(
                f"   {line}{'' if is_last_line else '<br>'}"
            )
        out_lines.append("</p>")
        paragraph_lines.clear()

    for line in segment.text.splitlines():
        is_blank_line = line.strip() == ""

        if is_blank_line:
            if is_in_paragraph():
                add_paragraph()
            else:
                out_lines.append("<br>")
        else:
            paragraph_lines.append(line)

    if is_in_paragraph():
        add_paragraph()

    return "\n".join(out_lines), {}


def _render_html_primary_cta_link_button(
        segment: models.PrimaryCTALinkButton
) -> tuple[str, dict[str, dict[str, str]]]:
    color = "#0a0"

    return textwrap.dedent(
        f'''\
        <a 
            class="cta-link-button--primary"
            href="{segment.url}"
        >
            {segment.text}
        </a>'''
    ), {
        ".cta-link-button--primary": {
            "display": "inline-block",
            "box-sizing": "border-box",
            "height": "48px",
            "margin": "0 0 12px",
            "padding": "14px",
            "line-height": "16px",
            "border": f"2px solid {color}",
            "border-radius": "24px",
            "color": f"{color} !important",
            "font-family": "sans-serif",
            "font-weight": "bold",
            "text-decoration": "none !important",
        },
        ".cta-link-button--primary:hover": {
            "color": "#fff !important",
            "background-color": color,
            "transform": "scale(1.05)"
        }
    }


def _normalize_template(template_: TemplateDict | str) -> TemplateDict:
    if type(template_) is str:
        return _read_template_dict_from_json_file(template_)

    return template_


def _read_template_dict_from_json_file(json_file_name: str) -> TemplateDict:
    path = Path(__file__).parent / "templates" / f"{json_file_name}.json"

    with open(path, "r") as f:
        return json.load(f)


def _validate_template(template_: TemplateDict) -> None:
    if (
        type(template_) is not dict
        or "header" not in template_
        or "body" not in template_
        or type(template_["header"]) is not list
        or type(template_["body"]) is not list
        or not all(
            (
                type(segment) is dict
                and "type" in segment
            )
            for segment in template_["header"] + template_["body"]
        )
    ):
        raise ValueError(
            f"Invalid email template '{template_}'"
        )


def _convert_header_templates_to_models(
        segment_template_dicts: list[SegmentDict],
        template_fill_obj: Any
) -> Iterable[models.HeaderSegment]:
    yield from cast(Iterable[models.HeaderSegment], _convert_dict_templates_to_models(
        "header",
        models.get_header_segment_by_type,
        segment_template_dicts,
        template_fill_obj,
    ))


def _convert_body_templates_to_models(
        segment_template_dicts: list[SegmentDict],
        template_fill_obj: Any
) -> Iterable[models.BodySegment]:
    yield from cast(Iterable[models.BodySegment], _convert_dict_templates_to_models(
        "body",
        models.get_body_segment_by_type,
        segment_template_dicts,
        template_fill_obj,
    ))


def _convert_dict_templates_to_models(
        path: str,
        get_model_by_type: Callable[[str], Type[models.Segment]],
        segment_template_dicts: list[SegmentDict],
        template_fill_obj: Any,
) -> Iterable[models.Segment]:
    for segment_template_dict in segment_template_dicts:
        segment_dict = _fill_in_segment_template_dict(
            path,
            template_fill_obj,
            segment_template_dict,
        )

        segment_class = get_model_by_type(segment_template_dict["type"])

        yield segment_class(**segment_dict)


def _fill_in_segment_template_dict(
        parent_path: str,
        template_fill_obj: Any,
        template_dict: SegmentDict,
) -> SegmentDict:
    filled_dict = {}
    for key, value in template_dict.items():
        if type(value) is str:
            filled_dict[key] = _normalize_text(template.replace(
                value,
                template_fill_obj,
                f"{parent_path}.{template_dict['type']}"
            ))
        # Allow multiline text to be expressed as a list of strings
        elif isinstance(value, Sequence) and all(type(item) is str for item in value):
            filled_dict[key] = _normalize_text(template.replace(
                "\n".join(value),
                template_fill_obj,
                f"{parent_path}.{template_dict['type']}"
            ))
        else:
            filled_dict[key] = value

    return filled_dict


def _normalize_text(text: str) -> str:
    text = _put_paragraphs_on_single_lines(text)
    text = _enforce_single_spaces_between_words(text)
    text = text.strip()  # Remove leading and trailing whitespace

    return text


def _put_paragraphs_on_single_lines(
        text_with_multiline_paragraphs: str,
        force_line_break_ending="\\",
) -> str:
    output_line_segments: list[str] = []
    output_lines: list[str] = []

    def line_has_ended():
        return len(output_line_segments) == 0

    def end_line() -> None:
        single_paragraph_line_segments: list[str] = []

        for line in output_line_segments:
            single_paragraph_line_segments.append(line.strip())

        output_lines.append(" ".join(single_paragraph_line_segments))

        output_line_segments.clear()

    for line in text_with_multiline_paragraphs.splitlines():
        is_blank = line.strip() == ""
        ends_with_forced_line_break = line.rstrip().endswith(force_line_break_ending)

        if ends_with_forced_line_break:
            output_line_segments.append(line.rstrip().removesuffix(force_line_break_ending))
            end_line()
        elif is_blank:
            if not line_has_ended():
                end_line()

            output_lines.append("")
        else:
            output_line_segments.append(line)

    if not line_has_ended():
        end_line()

    return "\n".join(output_lines)


def _enforce_single_spaces_between_words(text: str) -> str:
    output_chars: list[str] = []
    last_char_was_space = False

    for char in text:

        if char == " ":

            if last_char_was_space:
                continue

            last_char_was_space = True
        else:
            last_char_was_space = False

        output_chars.append(char)

    return "".join(output_chars)


# Unfortunately python's textwrap.wrap function does not
# seem to wrap lines as intended :(
def _wrap_lines(text: str, width: int) -> str:
    wrap_chars = {" ", "-"}

    output_chars: list[str] = []
    last_wrap_char: str | None = None
    chars_since_last_wrap_char: list[str] = []
    current_line_len = 0

    def can_wrap_line() -> bool:
        return last_wrap_char is not None

    def add_line_break() -> None:
        nonlocal last_wrap_char
        nonlocal current_line_len

        if can_wrap_line():
            append_chars_since_last_wrap_char(try_wrap=False)

        output_chars.append("\n")
        last_wrap_char = None
        current_line_len = 0

    def append_chars_since_last_wrap_char(try_wrap: bool) -> None:
        nonlocal current_line_len
        nonlocal last_wrap_char

        if try_wrap and can_wrap_line():
            if wrap_chars != " ":
                output_chars.append(last_wrap_char)

            output_chars.append("\n")
            last_wrap_char = None

            i = 0
            while i < len(chars_since_last_wrap_char) and chars_since_last_wrap_char[i] == " ":
                i += 1

            current_line_len = 0
            while i < len(chars_since_last_wrap_char):
                output_chars.append(chars_since_last_wrap_char[i])
                i += 1
                current_line_len += 1

        else:
            if last_wrap_char is not None:
                output_chars.append(last_wrap_char)

            output_chars.extend(chars_since_last_wrap_char)

        chars_since_last_wrap_char.clear()

    for char in text:
        if char == "\n":
            add_line_break()
            continue

        if char in wrap_chars:
            append_chars_since_last_wrap_char(try_wrap=False)
            last_wrap_char = char
        elif can_wrap_line():
            chars_since_last_wrap_char.append(char)
        else:
            output_chars.append(char)

        current_line_len += 1
        if current_line_len >= width:
            append_chars_since_last_wrap_char(try_wrap=True)

    if can_wrap_line():
        append_chars_since_last_wrap_char(try_wrap=False)

    return "".join(output_chars)


if __name__ == "__main__":

    def manually_test_send_mail():
        print(f"Testing {send_mail.__name__}")

        to = input("Enter recipient's email address: ")

        send_mail(
            to,
            {
                "header": [
                    {
                        "type": "subject",
                        "text": "{ project_name } test email"
                    }
                ],
                "body": [
                    {
                        "type": "text",
                        "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
                    },
                    {
                        "type": "primary_cta_link_button",
                        "text": "CTA Text",
                        "url": "{ .url }"
                    }
                ]
            },
            {
                "project_name": "HWR Tierartzt Finder",
                "body": {
                    "primary_cta_link_button": {
                        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                    }
                }
            }
        )

    manually_test_send_mail()
