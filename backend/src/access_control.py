import json
from collections.abc import Callable
import jwt
from typing import Literal, cast, Iterable, NoReturn

import config
from utils import typing_
from utils.human_readable import human_readable

Role = Literal[
    "test:frontend_user_with_verified_email",
    "test:form_website_user",
    "test:customer_management",
    "prod:frontend_user_with_verified_email",
    "prod:form_website_user",
    "prod:customer_management"
]

Permission = Literal[
    "create",
    "update",
    "read",
    "delete",
]

ObjectName = str


_ROLE = cast(frozenset[Role], frozenset(typing_.extract_strings_from_type(Role)))
_PERMISSION = cast(frozenset[Permission], frozenset(typing_.extract_strings_from_type(Permission)))

_object_names = set()

_granted_permissions: dict[Role, dict[ObjectName, set[Permission]]] = {}


class AccessDenied(Exception):
    pass


def register_object(name: str) -> None:
    _object_names.add(name)


def grant_permission(
        roles: Role | Iterable[Role],
        objects: ObjectName | Iterable[ObjectName],
        permissions: Permission | Iterable[Permission],
) -> None:
    _run_operations(_grant_single_permission, roles, objects, permissions)


def revoke_permission(
        roles: Role | Iterable[Role],
        objects: ObjectName | Iterable[ObjectName],
        permissions: Permission | Iterable[Permission],
) -> None:
    _run_operations(_revoke_single_permission, roles, objects, permissions)


def generate_jwt_for_role(role: Role) -> str:
    role = ensure_role(role)

    role_permissions = _granted_permissions[role]

    payload = {
        "role": role,
        "permissions": json.dumps({
            object_: sorted(object_permissions)
            for object_, object_permissions
            in role_permissions.items()
        })
    }
    secret_key = config.get().access_control.jwt_secret

    # Uses HS256 which is symmetric.
    # It would be better to use ECDSA or a strong RSA (at least 2048)
    # and implement client side verification of the token's origin
    # using the public key.
    return jwt.encode(payload, key=secret_key, algorithm="HS256")


def verify_access(
        object_: ObjectName,
        expected_permission: Permission,
        jwt_: str
) -> None | NoReturn:
    secret_key = config.get().access_control.jwt_secret

    try:
        payload = jwt.decode(jwt_, secret_key, algorithms=["HS256"])
    except jwt.exceptions.InvalidTokenError as err:
        raise AccessDenied(
            f"Access to object '{object_}' denied. "
            f"Invalid JWT"
        ) from err

    role = payload["role"]
    role_permissions_json = json.loads(payload["permissions"])
    role_permissions = {
        object_: set(object_permissions)
        for object_, object_permissions
        in role_permissions_json.items()
    }

    error_message = (
        f"Role '{role}' is not granted '{expected_permission}' "
        f"on object '{object_}'"
    )

    if object_ not in role_permissions:
        raise AccessDenied(error_message)

    object_permissions = role_permissions[object_]

    if expected_permission in object_permissions:
        return

    raise AccessDenied(error_message)


def has_access_explained(
        object_: ObjectName,
        expected_permission: Permission,
        jwt_: str
) -> tuple[bool, str]:
    try:
        verify_access(object_, expected_permission, jwt_)
    except AccessDenied as err:
        return False, str(err)

    return True, "Access Verified: Has access"


def has_access(
        object_: ObjectName,
        expected_permission: Permission,
        jwt_: str
) -> bool:
    return has_access_explained(object_, expected_permission, jwt_)[0]


def all_roles() -> frozenset[Role]:
    return _ROLE


def all_permissions() -> frozenset[Permission]:
    return _PERMISSION


def all_objects() -> frozenset[str]:
    return frozenset(_object_names)


def ensure_role(role: str) -> Role | NoReturn:
    if role not in all_roles():
        raise ValueError(
            f"Role '{role}' does not exist, "
            f"must be one of {human_readable(all_roles()).quoted().ored()}"
        )

    return cast(Role, role)


def ensure_permission(permission: str) -> Permission | NoReturn:
    if permission not in all_permissions():
        raise ValueError(
            f"Permission '{permission}' does not exist, "
            f"must be one of {human_readable(all_permissions()).quoted().ored()}"
        )

    return cast(Permission, permission)


def ensure_object(object_: str) -> ObjectName | NoReturn:
    if object_ not in all_objects():
        raise ValueError(
            f"Object '{object_}' has not been registered, "
            f"must be one of {human_readable(all_objects()).quoted().ored()}"
        )

    return cast(ObjectName, object_)


# Helpers
# =============================================================================

def _run_operations(
        base_operation: Callable[[Role, ObjectName, Permission], None],
        roles: Role | Iterable[Role],
        objects: ObjectName | Iterable[ObjectName],
        permissions: Permission | Iterable[Permission],
) -> None:
    if type(roles) is str:
        roles = [roles]

    if type(objects) is str:
        objects = [objects]

    if type(permissions) is str:
        permissions = [permissions]

    for role in roles:
        for object_ in objects:
            for permission in permissions:
                role = ensure_role(role)
                object_ = ensure_object(object_)
                permission = ensure_permission(permission)

                base_operation(role, object_, permission)


# To simplify business logic operations should be idempotent.
# I.e. they should function the same regardless if the system's state.
# -> Granting permissions that have already been granted is ok
# -> Revoking permissions that were never granted does nothing

def _grant_single_permission(
        role: Role,
        object_: ObjectName,
        permission: Permission
) -> None:
    if role not in _granted_permissions:
        _granted_permissions[role] = {}

    role_permission = _granted_permissions[role]

    if object_ not in role_permission:
        role_permission[object_] = set()

    object_permissions = role_permission[object_]

    object_permissions.add(permission)


def _revoke_single_permission(
        role: Role,
        object_: ObjectName,
        permission: Permission
) -> None:
    if role not in _granted_permissions:
        return

    role_permission = _granted_permissions[role]

    if object_ not in role_permission:
        return

    object_permissions = role_permission[object_]

    try:
        object_permissions.remove(permission)
    except KeyError:  # We do nothing if the permission was never granted
        pass
