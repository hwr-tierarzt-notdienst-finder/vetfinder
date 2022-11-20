import string

from .db import DB, Repository, TokenDoesNotExist, TokenAlreadyExists
from .tui import TUI


class Admin:
    db: DB
    tui: TUI

    def __init__(
            self,
            db: DB | None = None,
            tui: TUI | None = None
    ) -> None:
        self.db = db or DB()
        self.tui = tui or TUI()

    def main(self) -> None:
        try:
            while True:
                action = self.tui.ask([
                    mange_vet_email_tokens_action := "Manage vet email tokens",
                    manage_vet_collection_tokens_action := "Manage vet collection tokens",
                    save_action := "Save changes",
                    exit_action := "Exit"
                ])

                if action == mange_vet_email_tokens_action:
                    self.mange_vet_email_tokens()
                elif action == manage_vet_collection_tokens_action:
                    self.manage_vet_collection_tokens()
                elif action == save_action:
                    self.save()
                elif action == exit_action:
                    break
                else:
                    raise RuntimeError(f"Unexpected action '{action}'")
        except KeyboardInterrupt:
            pass

        if self.tui.ask_yes_no("Save before exiting?"):
            self.save()
        else:
            self.tui.display_text("Changes were discarded!")

    def mange_vet_email_tokens(self) -> None:
        action = self.tui.ask([
            show_token_action := "Show token for email address",
            show_all_action := "Show all",
            generate_token_action := "Generate token for new email address",
            replace_token_action := "Replace token for existing email address",
            change_token_id_action := "Change email address",
            delete_token_action := "Delete email address",
            exit_action := "Exit",
        ])

        while True:
            try:
                if action == show_token_action:

                    token_id = self.capture_email_address()

                    token = self.db.vet_email.find(token_id).value

                    self.tui.display_text(token)

                elif action == show_all_action:

                    for token in self.db.vet_email.all():
                        self.tui.display_text(f"id='{token.id_}' token='{token.value}'")

                elif action == generate_token_action:

                    token_id = self.capture_email_address()

                    token = self.db.vet_email.generate_token(token_id)

                    self.tui.display_text(
                        f"Generated token '{token}' for email address '{token_id}'"
                    )

                elif action == replace_token_action:

                    token_id = self.capture_email_address()

                    old_token = self.db.vet_email.find(token_id).value
                    if not self.confirm_destructive_action(
                            f"replace old token '{old_token}' for email address '{token_id}'"
                    ):
                        self.tui.display_text("Aborting")
                        break

                    new_token = self.db.vet_email.replace_token(token_id)

                    self.tui.display_text(
                        f"Generated new token '{new_token}' for email address '{token_id}'"
                    )

                elif action == change_token_id_action:

                    old_token_id = self.capture_email_address("Enter old email address:")
                    new_token_id = self.capture_email_address("Enter new email address:")

                    if not self.confirm_destructive_action(
                            f"replace old email address '{old_token_id}' with '{new_token_id}'"
                    ):
                        self.tui.display_text("Aborting")
                        break

                    self.db.vet_email.change_token_id(old_token_id, new_token_id)

                elif action == delete_token_action:

                    token_id = self.capture_email_address()

                    if not self.confirm_destructive_action(
                            f"delete token for email address '{token_id}'"
                    ):
                        self.tui.display_text("Aborting")
                        break

                    self.db.vet_email.delete_token(token_id)

                elif action == exit_action:
                    break

                else:
                    raise RuntimeError(f"Unexpected vet email token action '{action}'")

            except (TokenAlreadyExists, TokenDoesNotExist) as err:
                self.tui.display_text(f"Action '{action}' was unsuccessful!")
                self.tui.display_text(f"Error: {err}")
                self.tui.display_text("Please try again!")
            else:
                break

    def manage_vet_collection_tokens(self) -> None:
        action = self.tui.ask([
            show_token_action := "Show vet collection token",
            show_all_action := "Show all",
            generate_token_action := "Generate token for new vet collection",
            replace_token_action := "Replace token for existing vet collection",
            change_token_id_action := "Change vet collection name",
            delete_token_action := "Delete vet collection",
            exit_action := "Exit",
        ])

        while True:
            try:
                if action == show_token_action:

                    token_id = self.capture_vet_collection_name()

                    token = self.db.vet_collection.find(token_id).value

                    self.tui.display_text(token)

                elif action == show_all_action:

                    for token in self.db.vet_collection.all():
                        self.tui.display_text(f"id='{token.id_}' token='{token.value}'")

                elif action == generate_token_action:

                    token_id = self.capture_vet_collection_name()

                    token = self.db.vet_collection.generate_token(token_id)

                    self.tui.display_text(
                        f"Generated token '{token}' for vet collection '{token_id}'"
                    )

                elif action == replace_token_action:

                    token_id = self.capture_vet_collection_name()

                    old_token = self.db.vet_collection.find(token_id).value
                    if not self.confirm_destructive_action(
                            f"replace old token '{old_token}' for vet collection '{token_id}'"
                    ):
                        self.tui.display_text("Aborting")
                        break

                    new_token = self.db.vet_collection.replace_token(token_id)

                    self.tui.display_text(
                        f"Generated new token '{new_token}' for vet collection '{token_id}'"
                    )

                elif action == change_token_id_action:

                    old_token_id = self.capture_vet_collection_name("Enter old vet collection name:")
                    new_token_id = self.capture_vet_collection_name("Enter new vet collection name:")

                    if not self.confirm_destructive_action(
                            f"replace old vet collection name '{old_token_id}' with '{new_token_id}'"
                    ):
                        self.tui.display_text("Aborting")
                        break

                    self.db.vet_collection.change_token_id(old_token_id, new_token_id)

                elif action == delete_token_action:

                    token_id = self.capture_vet_collection_name()

                    if not self.confirm_destructive_action(
                            f"delete token for vet collection '{token_id}'"
                    ):
                        self.tui.display_text("Aborting")
                        break

                    self.db.vet_collection.delete_token(token_id)

                elif action == exit_action:
                    break

                else:
                    raise RuntimeError(f"Unexpected vet collection token action '{action}'")

            except (TokenAlreadyExists, TokenDoesNotExist) as err:
                self.tui.display_text(f"Action '{action}' was unsuccessful!")
                self.tui.display_text(f"Error: {err}")
                self.tui.display_text("Please try again!")
            else:
                break

    def save(self) -> None:
        self.db.flush()
        self.tui.display_text("Saved changes")

    def capture_email_address(self, prompt: str = "Enter email address:") -> str:
        return self.tui.ask(
            prompt,
            answer_is_correct=is_email,
            answer_is_wrong_text=(
                "Email address must contain '@', '.' and no whitespace characters. "
                "Please try again!"
            )
        )

    def capture_vet_collection_name(self, prompt: str = "Enter vet collection name:") -> str:
        return self.tui.ask(
            prompt,
            answer_is_correct=only_contains_lowercase_letters_or_underscores,
            answer_is_wrong_text=(
                "Vet collection name can only contain lowercase letters and underscores. "
                "Please try again!"
            )
        )

    def confirm_destructive_action(self, action: str) -> bool:
        return self.tui.ask_yes_no(
            f"Are you sure, you want to {action}?"
        )


def is_email(s: str) -> bool:
    return (
            "@" in s
            and "." in s
            and not any(char.isspace() for char in s)
    )


def only_contains_lowercase_letters_or_underscores(s: str) -> bool:
    charset = string.ascii_lowercase + "_"

    return all(char in charset for char in s)
