from __future__ import annotations

from collections.abc import Mapping, Iterable, Callable
from dataclasses import dataclass
from functools import partial
from typing import overload, Any, ClassVar, Protocol


class CoreUI(Protocol):

    def display_text(self, text: str) -> None:
        ...

    def capture_input(self, prompt: str = "") -> str:
        ...

    def ask(
            self,
            question: str | None = None,
            choices: list[Choice] | None = None,
            answer_prompt: str | None = None,
    ) -> str:
        if question is not None:
            self.display_question(question)

        if choices is not None:
            self.display_choices(choices)

        return self.prompt_answer(answer_prompt)

    def display_question(self, question: str) -> None:
        self.display_text(question)

    def display_choices(self, choices: list[Choice]) -> None:
        for choice in choices:
            if choice.answer_prompt is not None:
                self.display_text(f"{choice.answer_prompt}) {choice.text}")
            else:
                self.display_text(choice.text)

    def prompt_answer(self, answer_prompt: str | None = None) -> str:
        if answer_prompt is None:
            answer_prompt = ""

        answer_prompt += "> "

        return self.capture_input(answer_prompt)

    def prompt_retry_answer(
            self,
            *,
            answer_prompt: str | None = None,
            answer_is_wrong_text: str | None = None,
    ) -> str:
        if answer_is_wrong_text is None:
            answer_is_wrong_text = "Wrong answer, please try again."

        self.display_text(answer_is_wrong_text)

        return self.prompt_answer(answer_prompt)


class CLI(CoreUI):

    def display_text(self, text: str) -> None:
        print(text)

    def capture_input(self, prompt: str = "") -> str:
        return input(prompt)


class TUI:

    _ChoiceDefinition = str | tuple[str] | tuple[str, str] | tuple[str, Iterable[str], str]

    _core_ui: CoreUI

    def __init__(self, core_ui: CoreUI | None = None) -> None:
        if core_ui is None:
            self._core_ui = CLI()
        else:
            self._core_ui = core_ui

    def display_text(self, text: str) -> None:
        self._core_ui.display_text(text)

    def capture_input(self, prompt: str = "") -> str:
        return self._core_ui.capture_input(prompt)

    @overload
    def ask(
            self,
            question: str,
            answer_is_correct: Callable[[str], bool] | None = None,
            accepted_answers: Iterable[str] | None = None,
            retry_if_wrong: bool = True,
            max_reties: int = 10,
            return_if_wrong: str | None = None,
            answer_prompt: str | None = None,
            answer_is_wrong_text: str | None = None,
            ignore_case: bool = True,
            normalize_whitespace: bool = True,
    ) -> str:
        ...

    @overload
    def ask(
            self,
            choices: Iterable[_ChoiceDefinition],
            answer_is_correct: Callable[[str], bool] | None = None,
            accepted_answers: Iterable[str] | None = None,
            retry_if_wrong: bool = True,
            max_reties: int = 10,
            return_if_wrong: str | None = None,
            answer_prompt: str | None = None,
            answer_is_wrong_text: str | None = None,
            ignore_case: bool = True,
            normalize_whitespace: bool = True,
    ) -> str:
        ...

    @overload
    def ask(
            self,
            choices: Mapping[str, _ChoiceDefinition],
            answer_is_correct: Callable[[str], bool] | None = None,
            accepted_answers: Iterable[str] | None = None,
            retry_if_wrong: bool = True,
            max_reties: int = 10,
            return_if_wrong: str | None = None,
            answer_prompt: str | None = None,
            answer_is_wrong_text: str | None = None,
            ignore_case: bool = True,
            normalize_whitespace: bool = True,
    ) -> str:
        ...

    @overload
    def ask(
            self,
            question: str,
            choices: Iterable[str | tuple[str, str]],
            answer_is_correct: Callable[[str], bool] | None = None,
            accepted_answers: Iterable[str] | None = None,
            retry_if_wrong: bool = True,
            max_reties: int = 10,
            return_if_wrong: str | None = None,
            answer_prompt: str | None = None,
            answer_is_wrong_text: str | None = None,
            ignore_case: bool = True,
            normalize_whitespace: bool = True,
    ) -> str:
        ...

    @overload
    def ask(
            self,
            question: str,
            choices: Mapping[str, _ChoiceDefinition],
            answer_is_correct: Callable[[str], bool] | None = None,
            accepted_answers: Iterable[str] | None = None,
            retry_if_wrong: bool = True,
            max_reties: int = 10,
            return_if_wrong: str | None = None,
            answer_prompt: str | None = None,
            answer_is_wrong_text: str | None = None,
            ignore_case: bool = True,
            normalize_whitespace: bool = True,
    ) -> str:
        ...

    def ask(
            self,
            *args: str | Iterable[_ChoiceDefinition] | Mapping[str, _ChoiceDefinition],
            answer_is_correct: Callable[[str], bool] | None = None,
            accepted_answers: Iterable[str] | None = None,
            retry_if_wrong: bool = True,
            max_reties: int = 10,
            return_if_wrong: str | None = None,
            answer_prompt: str | None = None,
            answer_is_wrong_text: str | None = None,
            ignore_case: bool = True,
            normalize_whitespace: bool = True,
    ) -> str:
        answer_checks: list[Callable[[str], bool]] = []

        def answer_passes_all_checks(answer: str) -> bool:
            return all(check(answer) for check in answer_checks)

        if answer_is_correct is not None:
            if accepted_answers is not None:
                raise ValueError(
                    "'accepted_answers' cannot be set "
                    "if 'answer_is_correct' is set "
                    f"when calling {self.__class__.__name__}.{self.ask.__name__}"
                )

            answer_checks.append(answer_is_correct)

        elif accepted_answers is not None:

            def answer_is_in_accepted_answers(answer: str) -> bool:
                for accepted_answer in accepted_answers:
                    if ignore_case:
                        accepted_answer = accepted_answer.lower()
                        answer = answer.lower()

                    if normalize_whitespace:
                        accepted_answer = _normalize_whitespace(accepted_answer)
                        answer = _normalize_whitespace(answer)

                    if answer == accepted_answer:
                        return True

                return False

            answer_checks.append(answer_is_in_accepted_answers)

        if retry_if_wrong is False:
            max_reties = 0

        question_or_none, choices_or_none = self._normalize_ask_args(
            args,
            ignore_case=ignore_case,
            normalize_whitespace=normalize_whitespace,
        )

        if (choices := choices_or_none) is not None:

            def at_least_on_choice_has_answer(answer: str) -> bool:
                for choice_id, choice in choices.items():
                    if choice.accepts_any_answer():
                        return True

                    if accepted_answers is not None:
                        for accepted_answer in accepted_answers:
                            if not answer_is_correct(accepted_answer):
                                raise ValueError(
                                    f"Choice {choice} accepted answer '{accepted_answer}' conflicts with "
                                    "general correct answer check "
                                    f"for {self.__class__.__name__}.{self.ask.__name__}"
                                )

                    if choice.has_answer(answer):
                        return True

                return False

            answer_checks.append(at_least_on_choice_has_answer)

        is_retry = False
        while True:
            if not is_retry:
                answer = self._core_ui.ask(
                    question=question_or_none,
                    choices=choices_or_none and list(choices_or_none.values()),
                    answer_prompt=answer_prompt
                )
            else:
                answer = self._core_ui.prompt_retry_answer(
                    answer_prompt=answer_prompt,
                    answer_is_wrong_text=answer_is_wrong_text,
                )

            if answer_passes_all_checks(answer):
                if choices_or_none is None:
                    return answer

                for choice_id, choice in choices_or_none.items():
                    if choice.has_answer(answer):
                        return choice_id

            if max_reties == 0:
                break

            max_reties -= 1
            is_retry = True

        if return_if_wrong:
            return return_if_wrong

        raise WrongAnswer

    def ask_yes_no(
            self,
            question: str,
            retry_if_wrong: bool = True,
            max_reties: int = 10,
            return_if_wrong: str | None = None,
    ) -> bool:
        return self.ask(
            f"{question} [y/n]:",
            accepted_answers={"y", "n", "yes", "no"},
            retry_if_wrong=retry_if_wrong,
            return_if_wrong=return_if_wrong,
            max_reties=max_reties,
        ) in {"y", "yes"}

    def _normalize_ask_args(
            self,
            args: tuple[Any, ...],
            *,
            ignore_case: bool,
            normalize_whitespace: bool,
    ) -> tuple[str | None, dict[str, Choice] | None]:
        normalize_choices = partial(
            self._normalize_choices_arg,
            ignore_case=ignore_case,
            normalize_whitespace=normalize_whitespace,
        )

        if len(args) == 1:
            errors: list[Exception] = []

            try:
                return self._normalize_question_ask_arg(args[0]), None
            except (ValueError, TypeError) as err:
                errors.append(err)

            try:
                return None, normalize_choices(args[0])
            except (ValueError, TypeError) as err:
                errors.append(err)

            if len(errors) == 2:
                raise errors[0] from errors[1]

            raise errors[0]

        if len(args) == 2:
            return self._normalize_question_ask_arg(args[0]), normalize_choices(args[1])

        raise ValueError(
            f"{self.__class__.__name__}.{self.ask.__name__} "
            f"expects 1 or 2 arguments, not {len(args)}"
        )

    def _normalize_question_ask_arg(self, arg: Any) -> str:
        if type(arg) != str:
            raise TypeError(
                f"Question argument for {self.__class__.__name__}.{self.ask.__name__} "
                "must be a string"
            )

        return arg

    def _normalize_choices_arg(
            self,
            arg: Any,
            *,
            ignore_case: bool,
            normalize_whitespace: bool,
    ) -> dict[str, Choice]:
        get_id_and_normalize = partial(
            self._get_choice_id_and_normalize,
            ignore_case=ignore_case,
            normalize_whitespace=normalize_whitespace,
        )

        choices: dict[str, Choice] = {}

        if isinstance(arg, Iterable):
            for i, choice in enumerate(arg):
                choice_id, normalize_choice = get_id_and_normalize(choice, index=i)
                choices[choice_id] = normalize_choice

        elif isinstance(arg, Mapping):
            for i, (key, choice) in enumerate(arg.items()):
                choice_id, normalize_choice = get_id_and_normalize(choice, index=i, key=key)
                choices[choice_id] = normalize_choice

        else:
            raise TypeError(
                f"Choices argument for {self.__class__.__name__}.{self.ask.__name__} "
                "must be a sequence or mapping"
            )

        return choices

    def _get_choice_id_and_normalize(
            self,
            choice: Any,
            *,
            index: int | None = None,
            key: Any | None = None,
            ignore_case: bool,
            normalize_whitespace: bool,
    ) -> tuple[str, Choice]:

        # Normalize choice
        # ---------------

        _text: str | None = None
        _answer_prompt: str | None = None
        _accepted_answers: str | None = None

        # Normalization and validation logic for individual choice attributes
        # is implemented by the following getters and setters

        def set_text(val: Any) -> None:
            nonlocal _text

            if type(val) is not str:
                raise TypeError(
                    f"The choice text in {choice} for {self.__class__.__name__}.{self.ask.__name__} "
                    "must be a string"
                )

            _text = val

        def get_text() -> str:
            if _text is None:
                raise ValueError(
                    f"Choice {choice} for {self.__class__.__name__}.{self.ask.__name__} "
                    "does not contain the choice text"
                )

            return _text

        def set_answer_prompt(val: Any) -> None:
            nonlocal _answer_prompt

            if type(val) is not str:
                raise TypeError(
                    f"The answer prompt text in {choice} for {self.__class__.__name__}.{self.ask.__name__} "
                    "must be a string"
                )

            _answer_prompt = val

        def get_answer_prompt() -> str | None:
            if _answer_prompt is not None:
                return _answer_prompt

            if index is not None:
                return str(index + 1)

            return None

        def set_accepted_answers(val: Any) -> None:
            nonlocal _accepted_answers

            if not hasattr(val, "__iter__"):
                raise TypeError(
                    f"The accepted answers in {choice} for {self.__class__.__name__}.{self.ask.__name__} "
                    "must be a iterable"
                )

            accepted_answers_lst: list[str] = []
            for accepted_answer in val:
                if type(accepted_answer) is not str:
                    raise TypeError(
                        f"The accepted answer {accepted_answer} "
                        f"in {choice} for {self.__class__.__name__}.{self.ask.__name__} "
                        "must be a string"
                    )

                accepted_answers_lst.append(accepted_answer)

            _accepted_answers = frozenset(accepted_answers_lst)

        def get_accepted_answers() -> frozenset[str] | object:
            accepted_answers = Choice.ANY_ANSWER

            if _accepted_answers is not None:
                accepted_answers = _accepted_answers

            if index is not None:
                accepted_answers = frozenset(str(index + 1))

            return accepted_answers

        # We call the setters based on the denormalize choice value

        if type(choice) is str:
            set_text(choice)
        elif isinstance(choice, tuple):
            set_text(choice[0])

            try:
                set_answer_prompt(choice[1])
            except IndexError:
                pass

            try:
                set_accepted_answers(choice[2])
            except IndexError:
                pass

        # We populate the choice object with the values returned by the getters

        normalized_choice = Choice(
            ignore_case=ignore_case,
            normalize_whitespace=normalize_whitespace,
            text=get_text(),
            answer_prompt=get_answer_prompt(),
            accepted_answers=get_accepted_answers(),
        )

        # Get choice id
        # -------------

        if key is not None:
            if not type(key) == str:
                raise TypeError(
                    f"Choice id for {choice} for {self.__class__.__name__}.{self.ask.__name__} "
                    f"must be a string, not {type(key)}"
                )

            choice_id = key
        else:
            choice_id = get_text()

        return choice_id, normalized_choice


@dataclass(frozen=True)
class Choice:
    ANY_ANSWER: ClassVar[object] = object()

    ignore_case: bool
    normalize_whitespace: bool
    text: str
    answer_prompt: str | None
    accepted_answers: frozenset[str] | object

    def accepts_any_answer(self) -> bool:
        return self.accepted_answers == self.ANY_ANSWER

    def has_answer(self, answer: str) -> bool:
        if self.accepts_any_answer():
            return True

        for accepted_answer in self.accepted_answers:
            if self.ignore_case:
                answer = answer.lower()
                accepted_answer = accepted_answer.lower()

            if self.normalize_whitespace:
                answer = _normalize_whitespace(answer)
                accepted_answer = _normalize_whitespace(accepted_answer)

            if answer == accepted_answer:
                return True

        return False


class WrongAnswer(ValueError):
    pass


def _normalize_whitespace(s: str) -> str:
    s = s.strip()

    last_was_whitespace = False
    chars: list[str] = []
    for char in s:
        if char.isspace():
            last_was_whitespace = True
        elif last_was_whitespace:
            chars.append(" ")
            last_was_whitespace = False

        chars.append(char)

    return "".join(chars)
