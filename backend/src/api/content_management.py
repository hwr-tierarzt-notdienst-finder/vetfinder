from fastapi import APIRouter, Query

import vet_management


router = APIRouter(prefix="/content-management")


@router.get("/grant-vet-verification")
def grant_vet_verification(
        access_token: str = Query(alias="access-token"),
) -> str:
    vet_management.grant_vet_verification_by_content_management(
        access_token
    )

    return "Verification granted"


@router.get("/revoke-vet-verification")
def revoke_vet_verification(
        access_token: str = Query(alias="access-token"),
) -> str:
    vet_management.revoke_vet_verification_by_content_management(
        access_token
    )

    return "Verification revoked"


@router.get("/delete-vet")
def delete_vet(
        access_token: str = Query(alias="access-token"),
) -> str:
    vet_management.delete_vet_by_content_management(
        access_token
    )

    return "Deleted"
