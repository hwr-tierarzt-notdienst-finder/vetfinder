import jwt

import config


class JWTVerificationError(Exception):
    pass


_JWT_ALGORITHM = "HS256"


def generate_jwt(payload: dict[str, str]) -> str:
    secret_key = config.get().auth.jwt_secret

    return jwt.encode(payload, key=secret_key, algorithm=_JWT_ALGORITHM)


def verify_jwt_return_payload(
        jwt_: str
) -> dict[str, str]:
    secret_key = config.get().auth.jwt_secret

    try:
        payload = jwt.decode(jwt_, key=secret_key, algorithms=[_JWT_ALGORITHM])
    except jwt.InvalidTokenError as err:
        raise JWTVerificationError(
            f"Invalid token"
        ) from err

    return payload
