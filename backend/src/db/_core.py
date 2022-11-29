from __future__ import annotations

from typing import Any, TypeVar, Type, Callable, Generic, Iterable, TypedDict, ClassVar

from bson.objectid import ObjectId
import pymongo
from pydantic.main import BaseModel
from pymongo import MongoClient
from pymongo.database import Collection, Database, Mapping

from utils import cache
from models import ModelWithId
import config


_TBaseModel = TypeVar("_TBaseModel", bound=BaseModel)
_TInDbModel = TypeVar("_TInDbModel", bound=ModelWithId)


class BaseRepository(Generic[_TBaseModel, _TInDbModel]):
    _IN_DB_CLS: ClassVar[Type[_TInDbModel]]

    _collection: Collection[Mapping[str, Any]]

    def __init__(self, collection_name: str) -> None:
        self._collection = get_db()[collection_name]

    @property
    def in_db_cls(self) -> Type[_TInDbModel]:
        return self._IN_DB_CLS

    @property
    def collection(self) -> Collection[Mapping[str, Any]]:
        return self._collection

    def insert(
            self,
            model: _TBaseModel
    ) -> _TInDbModel:
        insert_result = self.collection.insert_one(db_entry_from_model(model))

        return self.in_db_cls(
            **(model.dict() | {"id": str(insert_result.inserted_id)})
        )

    def find(
            self,
            what: dict | _TInDbModel | Iterable[_TBaseModel] | Callable[[dict], bool] | None = None,
            *,
            allow_none_for_all: bool = False,
    ) -> list[_TInDbModel]:
        mongo_query_results: list[dict]

        if what is None:
            if allow_none_for_all:
                raise ValueError(
                    "Find with no arguments cannot be used for findall "
                    "without passing allow_none_for_all=True"
                )

            return find_models(self.in_db_cls, self.collection, {})
        elif isinstance(what, ModelWithId):
            return find_models(self.in_db_cls, self.collection, {"_id": what.id})
        elif isinstance(what, dict):
            return find_models(self.in_db_cls, self.collection, what)

        errors: list[Exception] = []
        try:
            results: list[_TInDbModel] = []
            for subquery in what:
                results += self.find(subquery)

            return results
        except Exception as err:
            errors.append(err)

        try:
            condition = what

            results: list[_TInDbModel] = []
            for model in self.all():
                if condition(model):
                    results.append(model)

            return results
        except Exception as err:
            errors.append(err)

        if errors:
            raise ValueError(
                f"Unexpected argument '{what}' for find"
            ) from errors[0]

        raise RuntimeError

    def first(
            self,
            what: dict | _TInDbModel | Iterable[_TBaseModel] | Callable[[dict], bool] | None = None,
            *,
            allow_none_for_all: bool = False,
    ) -> _TInDbModel:
        return self.find(what, allow_none_for_all=allow_none_for_all)[0]

    def exactly_one(
            self,
            what: dict | _TInDbModel | Iterable[_TBaseModel] | Callable[[dict], bool] | None = None,
            *,
            allow_none_for_all: bool = False,
    ) -> _TInDbModel:
        models = self.find(what, allow_none_for_all=allow_none_for_all)

        if len(models) != 1:
            raise ValueError(
                f"More than result for find query with argument '{what}'"
            )

        return models[0]

    def all(self) -> list[_TInDbModel]:
        return self.find({})

    def delete_all(self) -> None:
        self.collection.drop()

    def delete_by_id(self, id_: str) -> None:
        self.collection.delete_one({"_id": ObjectId(id_)})

    def delete(self, model: _TInDbModel) -> None:
        return self.delete_by_id(model.id)

    def update(
            self,
            updated_model: _TInDbModel,
    ) -> _TInDbModel:
        self.delete(updated_model)
        self.insert(updated_model)

        return updated_model


class _DictWithId(TypedDict, total=False):
    id: str


@cache.return_singleton(populate_cache_on="prepopulate_called")
def get_db() -> Database[Mapping[str, Any]]:
    client = create_mongo_client()

    return client["db"]


def create_mongo_client() -> MongoClient:
    connection_str = get_connection_string()

    with pymongo.timeout(config.get().db.connection_ping_timeout):
        # Test connection to client
        client = MongoClient(connection_str)
        client.admin.command("ping")

    return client


def get_connection_string() -> str:
    db_config = config.get().db

    return f"mongodb://{db_config.root_username}:{db_config.root_password}@0.0.0.0:{db_config.port}"


def model_from_db_entry(
        in_db_cls: Type[_TInDbModel],
        entry: Mapping[str, Any]
) -> _TInDbModel:
    return in_db_cls(
        id=str(entry["_id"]),
        **entry
    )


def db_entry_from_model(
        model: _TInDbModel
) -> dict[str, Any]:
    dct = model.dict()
    if "id" in dct:
        del dct["id"]

    return dct


def find_result_as_models(
        in_db_cls: Type[_TInDbModel],
        result: pymongo.cursor.Cursor,
) -> list[_TInDbModel]:
    return [
        model_from_db_entry(in_db_cls, entry)
        for entry in result
    ]


def find_models(
        in_db_cls: Type[_TInDbModel],
        collection: Collection[Mapping[str, Any]],
        query: dict,
) -> list[_TInDbModel]:
    return find_result_as_models(in_db_cls, collection.find(query))
