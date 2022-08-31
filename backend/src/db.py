from typing import Any

import pymongo
from pymongo import MongoClient
from pymongo.database import Database, Mapping

from . import config


_db = None
def get_db() -> Database[Mapping[str, Any]]:
    global _db

    if _db is None:
        client = create_mongo_client()

        _db = client["db"]

    return _db


def create_mongo_client() -> MongoClient:
    connection_str = get_connection_string()

    with pymongo.timeout(config.get().db.connection_ping_timeout):
        # Test connection to client
        client = MongoClient(connection_str)
        client.admin.command("ping")

    return client


def get_connection_string() -> str:
    db_config = config.get().db

    return f"mongodb://{db_config.root_username}:{db_config.root_password}@127.0.0.1:{db_config.port}"
