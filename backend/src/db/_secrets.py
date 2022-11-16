from models import Secret, SecretInDb
from ._core import BaseRepository


class _Repository(BaseRepository[Secret, SecretInDb]):
    _IN_DB_CLS = SecretInDb


repository = _Repository("secrets")
