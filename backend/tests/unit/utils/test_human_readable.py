from src.utils.human_readable import human_readable, Config


class TestHumanReadable:

    def test_quotes_string_correctly(self) -> None:
        assert str(human_readable("a")) == "a"
        assert str(human_readable("abc")) == "abc"
        assert str(human_readable("abc").quoted()) == "'abc'"
        assert str(human_readable("abc").quoted("single")) == "'abc'"
        assert str(human_readable("abc").quoted("double")) == '"abc"'
        assert str(human_readable("abc").quoted("code")) == "`abc`"
        assert str(human_readable("abc").single_quoted()) == "'abc'"
        assert str(human_readable("abc").double_quoted()) == '"abc"'
        assert str(human_readable("abc").code()) == "`abc`"

    def test_quotes_string_sequence_correctly(self) -> None:
        assert str(human_readable([])) == ""
        assert str(human_readable([]).quoted()) == "''"
        assert str(human_readable(["abc", "def"])) == "abc, def"
        assert str(human_readable(["abc", "def"]).quoted()) == "'abc, def'"
        assert str(human_readable(["abc", "def"]).quoted("single")) == "'abc, def'"
        assert str(human_readable(["abc", "def"]).quoted("double")) == '"abc, def"'
        assert str(human_readable(["abc", "def"]).quoted("code")) == "`abc, def`"
        assert str(human_readable(["abc", "def"]).single_quoted()) == "'abc, def'"
        assert str(human_readable(["abc", "def"]).double_quoted()) == '"abc, def"'
        assert str(human_readable(["abc", "def"]).code()) == "`abc, def`"

        assert str(human_readable([]).items_quoted()) == ""
        assert str(human_readable(["abc", "def"]).items_quoted()) == "'abc', 'def'"
        assert str(human_readable(["abc", "def"]).items_quoted("single")) == "'abc', 'def'"
        assert str(human_readable(["abc", "def"]).items_quoted("double")) == '"abc", "def"'
        assert str(human_readable(["abc", "def"]).items_quoted("code")) == "`abc`, `def`"
        assert str(human_readable(["abc", "def"]).items_single_quoted()) == "'abc', 'def'"
        assert str(human_readable(["abc", "def"]).items_double_quoted()) == '"abc", "def"'
        assert str(human_readable(["abc", "def"]).items_code()) == "`abc`, `def`"

        assert str(human_readable(["abc", "def"]).quoted().items_code()) == "'`abc`, `def`'"
        assert str(human_readable(["abc", "def"]).items_code().quoted()) == "'`abc`, `def`'"

    def test_uses_correct_separator(self) -> None:
        assert str(human_readable(["abc", "def", "ghi"]).separated(",")) == "abc, def, ghi"
        assert str(human_readable(["abc", "def", "ghi"]).separated("|")) == "abc | def | ghi"
        assert str(human_readable(["abc", "def", "ghi"]).comma_separated()) == "abc, def, ghi"
        assert str(human_readable(["abc", "def", "ghi"]).pipe_separated()) == "abc | def | ghi"

    def test_adds_conjunctions_to_sequence_correctly(self) -> None:
        assert str(human_readable([]).anded()) == ""
        assert str(human_readable(["abc"]).anded()) == "abc"
        assert str(human_readable(["abc", "def"]).anded()) == "abc and def"
        assert str(human_readable(["abc", "def", "ghi"]).with_conjunction("and")) == "abc, def and ghi"
        assert str(human_readable(["abc", "def", "ghi"]).with_conjunction("or")) == "abc, def or ghi"
        assert str(human_readable(["abc", "def", "ghi"]).with_conjunction("and/or")) == "abc, def and/or ghi"
        assert str(human_readable(["abc", "def", "ghi"]).anded()) == "abc, def and ghi"
        assert str(human_readable(["abc", "def", "ghi"]).ored()) == "abc, def or ghi"
        assert str(human_readable(["abc", "def", "ghi"]).and_ored()) == "abc, def and/or ghi"

    def test_shortens_sequence(self) -> None:
        assert str(human_readable(["1", "2", "3", "4", "5"]).shorten_if_longer_than(4)) == "1, 2, ..., 4, 5"
        assert str(human_readable(["1", "2", "3", "4", "5", "6"]).shorten_if_longer_than(4)) == "1, 2, ..., 5, 6"
        assert str(human_readable(["1", "2", "3", "4", "5", "6"]).shorten_if_longer_than(5)) == "1, 2, 3, ..., 5, 6"

    def test_converts_types(self) -> None:
        class Cls:
            pass

        assert str(human_readable([int, Cls, "foo"])) == "int, Cls, foo"

    def test_uses_configuration(self) -> None:
        assert str(human_readable("abc", Config(default_quote_style="double")).quoted()) == '"abc"'
        assert str(human_readable(["abc", "def"], Config(default_sequence_delimiter="|"))) == "abc | def"
        assert str(human_readable(
            ["1", "2", "3", "4", "5", "6"],
            Config(default_shorten_sequence_if_longer_than=5))
        ) == "1, 2, 3, ..., 5, 6"

