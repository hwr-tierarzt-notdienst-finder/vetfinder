import base64
import json

import pytest

import access_control


def test_can_deny() -> None:
    role: access_control.Role = "test:frontend_user_with_verified_email"
    object_with_access_granted_for_role = "unverified_vet_collection"
    object_with_access_denied_for_role = "verified_vet_collection"

    access_control.register_object(object_with_access_granted_for_role)
    access_control.grant_permission(
        role,
        object_with_access_granted_for_role,
        {"create", "update"}
    )

    jwt_ = access_control.generate_jwt_for_role(role)

    # Fails when trying to access object with no permission granted for role
    with pytest.raises(access_control.AccessDenied):
        access_control.verify_access(
            object_with_access_denied_for_role,
            "create",
            jwt_
        )

    # Fails when trying to access object using wrong permissions
    with pytest.raises(access_control.AccessDenied):
        access_control.verify_access(
            object_with_access_granted_for_role,
            "delete",
            jwt_,
        )

    # Fails when JWT has been tampered with
    header_part, payload_part, signature_part = jwt_.split(".")
    payload = json.loads(base64.urlsafe_b64decode(payload_part))
    role_permissions = json.loads(payload["permissions"])
    tampered_role_permissions = {**role_permissions}
    tampered_role_permissions[object_with_access_granted_for_role].append("delete")
    tampered_payload = {
        "role": payload["role"],
        "permissions": json.dumps(tampered_role_permissions)
    }
    tampered_payload_part = base64.urlsafe_b64encode(json.dumps(tampered_payload).encode("utf-8")).decode("utf-8")
    tampered_jwt = ".".join([header_part, tampered_payload_part, signature_part])

    assert jwt_.split(".")[0] == tampered_jwt.split(".")[0]  # Header is the same
    assert jwt_.split(".")[1] != tampered_jwt.split(".")[1]  # Payload is different
    assert jwt_.split(".")[2] == tampered_jwt.split(".")[2]  # Signature is the same

    with pytest.raises(access_control.AccessDenied):
        access_control.verify_access(
            object_with_access_granted_for_role,
            "create",
            tampered_jwt,
        )

def test_can_verify() -> None:
    role: access_control.Role = "test:frontend_user_with_verified_email"
    object_ = "unverified_vet_collection"

    access_control.register_object(object_)
    access_control.grant_permission(role, object_, {"create", "update"})

    jwt_ = access_control.generate_jwt_for_role(role)

    access_control.verify_access(object_, "create", jwt_)
    access_control.verify_access(object_, "update", jwt_)
