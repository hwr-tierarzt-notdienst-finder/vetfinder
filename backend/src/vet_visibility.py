from typing import cast

import auth
from constants import VET_VISIBILITIES
import paths
from types_ import VetVisibility


def generate_visibility_jwt(
        visibility: VetVisibility,
) -> str:
    return auth.generate_jwt({
        "visibility": visibility,
    })


def get_visibility_from_jwt(jwt: str) -> VetVisibility:
    return cast(
        VetVisibility,
        auth.verify_jwt_return_payload(jwt)["visibility"]
    )


def _write_visibility_jwts_to_file() -> None:
    content = "\n".join([
        f"{visibility}:{generate_visibility_jwt(visibility)}"
        for visibility in VET_VISIBILITIES
    ])

    with open(paths.find_backend() / "vet_visibility_tokens.txt", "w") as f:
        f.write(content)


_write_visibility_jwts_to_file()
