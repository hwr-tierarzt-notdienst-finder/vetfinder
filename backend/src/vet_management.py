import uuid
from dataclasses import dataclass
from typing import Literal, cast

import auth
import config
import db
import email_
import normalization.vet
import vet_visibility
from models import VetCreateOrOverwrite, Vet, RegistrationEmailInfo
from types_ import VetVisibility

Role = Literal[
    "form_user",
    "content_management",
]


class AccessDenied(Exception):
    pass


@dataclass(frozen=True)
class _AccessInfo:
    visibility: VetVisibility
    id: str


def send_registration_email(
        visibility_jwt: str,
        info: RegistrationEmailInfo,
) -> None:
    email_.send_vet_registration(
        info.email_address,
        _generate_access_token(
            _generate_new_id(),
            "form_user",
            vet_visibility.get_visibility_from_jwt(visibility_jwt)
        )
    )


def get_vet_by_form_user(
        jwt: str,
) -> Vet:
    access_info = allow_access_and_get_info(jwt, "form_user")

    return db.get_vet_by_id(access_info.visibility, access_info.id)


def create_or_update_vet_by_form_user(
        jwt: str,
        vet: VetCreateOrOverwrite,
) -> Vet:
    access_info = allow_access_and_get_info(jwt, "form_user")

    vet = normalization.vet.normalize(vet)

    vet_in_db = db.create_or_overwrite_vet(
        access_info.visibility,
        "unverified",
        access_info.id,
        vet,
    )

    content_management_jwt = _generate_access_token(
        vet_in_db.id,
        "content_management",
        access_info.visibility,
    )
    content_management_api_root_url = (
        f"{config.get().domain}:{config.get().fastapi.port}/content-management"
    )
    for management_email_address in config.get().content_management.email_addresses:
        email_.send_vet_management(
            management_email_address,
            f"{content_management_api_root_url}/grant-vet-verification?access-token={content_management_jwt}",
            f"{content_management_api_root_url}/revoke-vet-verification?access-token={content_management_jwt}",
            f"{content_management_api_root_url}/delete-vet?access-token={content_management_jwt}",
            vet_in_db.id,
            vet_in_db.dict(),
        )

    return vet_in_db


def grant_vet_verification_by_content_management(jwt: str) -> Vet:
    access_info = allow_access_and_get_info(jwt, "content_management")

    return db.change_vet_verification_status_by_id_if_exists(
        access_info.visibility,
        access_info.id,
        "verified",
    )


def revoke_vet_verification_by_content_management(jwt: str) -> Vet:
    access_info = allow_access_and_get_info(jwt, "content_management")

    return db.change_vet_verification_status_by_id_if_exists(
        access_info.visibility,
        access_info.id,
        "unverified",
    )


def delete_vet_by_content_management(
        jwt: str
) -> None:
    access_info = allow_access_and_get_info(jwt, "content_management")

    return db.delete_vet_by_id_if_exists(
        access_info.visibility,
        access_info.id,
    )


def allow_access_and_get_info(
        token: str,
        expected_role: Role,
) -> _AccessInfo:
    try:
        jwt_payload = auth.verify_jwt_return_payload(token)
    except auth.JWTVerificationError as err:
        raise AccessDenied from err

    if (role := jwt_payload.get("role", None)) != expected_role:
        raise AccessDenied(
            f"Could not allow access as role '{expected_role}'. "
            f"Expected role '{expected_role}', to '{role}'"
        )

    try:
        return _AccessInfo(
            id=jwt_payload["sub"],
            visibility=cast(VetVisibility, jwt_payload["visibility"]),
        )
    except KeyError as err:
        raise AccessDenied(
            f"Could not allow access as role '{expected_role}'. "
            f"Incomplete JWT payload"
        ) from err


def access_is_allowed(
        token: str,
        expected_role: Role,
) -> bool:
    try:
        allow_access_and_get_info(token, expected_role)
        return True
    except AccessDenied:
        return False


def _generate_new_id() -> str:
    return str(uuid.uuid4())


def _generate_access_token(
        id_: str,
        role: Role,
        visibility: VetVisibility,
) -> str:
    return auth.generate_jwt({
        "sub": id_,
        "role": role,
        "visibility": visibility,
    })
