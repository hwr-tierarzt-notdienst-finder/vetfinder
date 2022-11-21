from auth import token


def test_has_hashes_for_vets_collections() -> None:
    assert token.is_authentic("vets.hidden", "aaa") is False
    assert token.is_authentic("vets.public", "aaa") is False