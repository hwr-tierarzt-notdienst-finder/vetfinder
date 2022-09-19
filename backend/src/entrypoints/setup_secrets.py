import auth


def main() -> None:
    auth.token.ensure_system_has_tokens_and_token_hashes_saved()


if __name__ == '__main__':
    main()
