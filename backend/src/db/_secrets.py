from models import SecretInDb
from ._core import create_repo


repo = create_repo(
    SecretInDb,
    "secrets"
)
