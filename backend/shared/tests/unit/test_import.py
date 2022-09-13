import textwrap
from pathlib import Path

from shared import file_system
from shared import import_


def test_iter_submodules() -> None:
    temp_module_path = Path(__file__).parent / "temp_module"

    with file_system.temp_dir(
        temp_module_path,
        [
            {
                "type": "file",
                "name": "__init__.py",
                "contents": "",
            },
            {
                "type": "file",
                "name": "sub_module1.py",
                "contents": textwrap.dedent(
                    """
                    member_var = "a"
                    """
                )
            },
            {
                "type": "file",
                "name": "_hidden_sub_module1.py",
                "contents": textwrap.dedent(
                    """
                    member_var = "a"
                    """
                )
            },
            {
                "type": "file",
                "name": "sub_module2.py",
                "contents": textwrap.dedent(
                    """
                    member_var = "b"
                    """
                )
            },
            {
                "type": "file",
                "name": "sub_module3.py",
                "contents": textwrap.dedent(
                    """
                    member_var = "c"
                    """
                )
            },
            {
                "type": "file",
                "name": "__hidden_sub_module2.py",
                "contents": textwrap.dedent(
                    """
                    member_var = "a"
                    """
                )
            },
        ]
    ):
        import temp_module

        sub_modules = list(import_.iter_submodules(temp_module))

        assert len(sub_modules) == 3
        assert {
            module.__name__ for module in sub_modules
        } == {
            "temp_module.sub_module1",
            "temp_module.sub_module2",
            "temp_module.sub_module3",
        }
        for sub_module in sub_modules:
            if sub_module.__name__.endswith("sub_module1"):
                assert sub_module.member_var == "a"
            if sub_module.__name__.endswith("sub_module2"):
                assert sub_module.member_var == "b"
            if sub_module.__name__.endswith("sub_module3"):
                assert sub_module.member_var == "c"
