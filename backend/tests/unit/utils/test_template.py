import textwrap

from utils import template


def test_can_replace_simple_one_liner():
    assert template.replace("Value at {}", "end") == "Value at end"
    assert template.replace("{} at start", "Value") == "Value at start"
    assert template.replace("Value {} middle", "in") == "Value in middle"


def test_can_replace_template_using_paths():
    template_text = textwrap.dedent(
        """\
        value1={ value1 }
        value2={value2}
        nested={nested.0}"""
    )
    expected_output = textwrap.dedent(
        """\
        value1=value1
        value2=value2
        nested=nested_value"""
    )

    obj1 = {
        "value1": "value1",
        "value2": "value2",
        "nested": ["nested_value"]
    }

    class Obj2Cls:
        value1: str = "value1"
        value2: str = "value2"
        nested: list[str] = ["nested_value"]

    obj2 = Obj2Cls()

    assert template.replace(template_text, obj1) == expected_output
    assert template.replace(template_text, obj2) == expected_output


def test_can_replace_template_with_non_root_path():
    assert template.replace(
        textwrap.dedent(
            """\
            item.value1={ .value1 }
            item.value2={.value2}
            item.nested={.nested.0}
            root_value={root_value}"""
        ),
        {
            "root_value": "root_value",
            "item": {
                "value1": "value1",
                "value2": "value2",
                "nested": ["nested_value"]
            }
        },
        "item"
    ) == textwrap.dedent(
        """\
        item.value1=value1
        item.value2=value2
        item.nested=nested_value
        root_value=root_value"""
    )


def test_replace_can_use_alternative_characters():
    assert template.replace(
        textwrap.dedent(
            """\
            item.value1={{ value1 }}
            item.value2={{value2}}
            item.nested={{nested / 0}}
            item.nested=ESC{{nested / 0}}
            root_value={{/root_value}}"""
        ),
        {
            "root_value": "root_value",
            "item": {
                "value1": "value1",
                "value2": "value2",
                "nested": ["nested_value"]
            }
        },
        "/item",
        placeholder_start="{{",
        placeholder_end="}}",
        escape="ESC",
        path_sep="/",
        root_path_start="/",
        rel_path_start="",
    ) == textwrap.dedent(
        """\
        item.value1=value1
        item.value2=value2
        item.nested=nested_value
        item.nested={{nested / 0}}
        root_value=root_value"""
    )

    assert template.replace(
        textwrap.dedent(
            """\
            item.value1={{ value1 }}
            item.value2={{value2}}
            item.nested={{nested / 0}}
            item.nested=ESC{{nested / 0}}
            root_value={{/root_value}}"""
        ),
        {
            "root_value": "root_value",
            "item": {
                "value1": "value1",
                "value2": "value2",
                "nested": ["nested_value"]
            }
        },
        "/item",
        config=template.Config(
            placeholder_start="{{",
            placeholder_end="}}",
            escape="ESC",
            path_sep="/",
            root_path_start="/",
            rel_path_start="",
        )
    ) == textwrap.dedent(
        """\
        item.value1=value1
        item.value2=value2
        item.nested=nested_value
        item.nested={{nested / 0}}
        root_value=root_value"""
    )
