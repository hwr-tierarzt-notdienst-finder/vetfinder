from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import email_
import vet_management
from models import Vet, RegistrationEmailInfo, VetCreateOrOverwrite


router = APIRouter(prefix="/form")

security = HTTPBearer()


@router.post("/send-vet-registration-email")
def send_registration_email(
        info: RegistrationEmailInfo,
        credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    visibility_token = credentials.credentials

    try:
        vet_management.send_registration_email(
            visibility_token,
            info,
        )
    except email_.FailedToSend as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send email"
        ) from err

    return "Sent email"


@router.put("/create-or-overwrite-vet")
def create_or_overwrite_vet(
        vet: VetCreateOrOverwrite,
        credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Vet:
    access_token = credentials.credentials

    return vet_management.create_or_update_vet_by_form_user(
        access_token,
        vet,
    )
