from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, TypeVar, Type, Callable, Generic, Protocol, Iterable, TypedDict

from bson.objectid import ObjectId
import pymongo
from pydantic.main import BaseModel
from pymongo import MongoClient
from pymongo.database import Collection, Database, Mapping

from utils import cache
from models import InDbModel
import config


_TBaseModel = TypeVar("_TBaseModel", bound=BaseModel)
_TInDbModel = TypeVar("_TInDbModel", bound=InDbModel)


@dataclass(frozen=True)
class BaseRepository(Generic[_TBaseModel, _TInDbModel]):
    insert: Callable[[_TBaseModel], _TInDbModel]
    find: _RepositoryFind[_TInDbModel]
    first: _RepositoryFind[_TInDbModel]
    exactly_one: _RepositoryExactlyOne[_RepositoryExactlyOne]
    all: Callable[[], list[_TInDbModel]]
    update: _RepositoryUpdate[_TInDbModel]
    update_and_return_all: _RepositoryUpdateAndReturnAll[_TInDbModel]
    delete: Callable[[_TInDbModel], None]
    delete_all: Callable[[], None]
    delete_by_id: Callable[[str], None]
    get_collection: Callable[[], Collection[Mapping[str, Any]]]


class _RepositoryFind(Protocol[_TInDbModel]):

    def __call__(
            self,
            what: dict | _TInDbModel | Iterable[_TBaseModel] | Callable[[_TBaseModel], bool] | None = None,
            *,
            allow_none_for_all: bool = False,
    ) -> list[_TInDbModel]: ...


class _RepositoryFirst(Protocol[_TInDbModel]):

    def __call__(
            self,
            what: dict | Iterable[dict] | _TInDbModel | Iterable[_TBaseModel] | Callable[[dict], bool] | None = None,
            *,
            allow_none_for_all: bool = False,
    ) -> _TInDbModel: ...


class _RepositoryExactlyOne(Protocol[_TInDbModel]):

    def __call__(
            self,
            what: dict | Iterable[dict] | _TInDbModel | Iterable[_TBaseModel] | Callable[[dict], bool] | None = None,
            *,
            allow_none_for_all: bool = False,
    ) -> _TInDbModel: ...


class _RepositoryUpdate(Protocol[_TInDbModel]):

    def __call__(
            self,
            model: _TInDbModel,
            *,
            post_rollback: Iterable[Callable[[], Any]] | Callable[[], Any] | None = None,
    ) -> _TInDbModel: ...


class _RepositoryUpdateAndReturnAll(Protocol[_TInDbModel]):

    def __call__(
            self,
            model: _DictWithId | tuple[str, dict] | _TInDbModel,
            post_rollback: Iterable[Callable[[], Any]] | Callable[[], Any] | None = None,
    ) -> list[_TInDbModel]: ...


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

    return f"mongodb://{db_config.root_username}:{db_config.root_password}@127.0.0.1:{db_config.port}"


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


def collection_as_models(
        in_db_cls: Type[_TInDbModel],
        collection: Collection[Mapping[str, Any]],
) -> list[_TInDbModel]:
    return find_models(in_db_cls, collection, {})


def filtered_collection_as_models(
        in_db_cls: Type[_TInDbModel],
        collection: Collection[Mapping[str, Any]],
        condition: Callable[[Mapping[str, Any]], bool],
) -> list[_TInDbModel]:
    return [
        model_from_db_entry(in_db_cls, entry)
        for entry in collection
        if condition(entry)
    ]


_Repository = TypeVar("_Repository", bound=BaseRepository)


def create_repo(
        in_db_cls: Type[_TInDbModel],
        collection_name: str,
        *,
        repo_cls: Type[_Repository] = BaseRepository,
        create_extra_methods: Callable[[BaseRepository], Iterable[Callable[[Any], Any] | Callable[[Any, ...], Any]]] | None = None,
) -> BaseRepository[_TBaseModel, _TInDbModel]:
    if create_extra_methods is None:
        def create_extra_methods(base_repo: BaseRepository) -> Iterable[Callable[[Any, ...], Any]]:
            return []

    @cache.return_singleton
    def get_collection() -> Collection[Mapping[str, Any]]:
        db = get_db()

        return db[collection_name]

    def insert(model: _TBaseModel) -> _TInDbModel:
        collection = get_collection()

        insert_result = collection.insert_one(db_entry_from_model(model))

        return in_db_cls(
            id=str(insert_result.inserted_id),
            **model.dict()
        )

    def find(
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

            return find_models(in_db_cls, get_collection(), {})
        elif isinstance(what, InDbModel):
            return find_models(in_db_cls, get_collection(), {"_id": what.id})
        elif isinstance(what, dict):
            return find_models(in_db_cls, get_collection(), what)

        errors: list[Exception] = []
        try:
            results: list[_TInDbModel] = []
            for subquery in what:
                results += find(subquery)

            return results
        except Exception as err:
            errors.append(err)

        try:
            condition = what

            results: list[_TInDbModel] = []
            for model in all_():
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
            what: dict | _TInDbModel | Iterable[_TBaseModel] | Callable[[dict], bool] | None = None,
            *,
            allow_none_for_all: bool = False,
    ) -> _TInDbModel:
        return find(what, allow_none_for_all=allow_none_for_all)[0]

    def exactly_one(
            what: dict | _TInDbModel | Iterable[_TBaseModel] | Callable[[dict], bool] | None = None,
            *,
            allow_none_for_all: bool = False,
    ) -> _TInDbModel:
        models = find(what, allow_none_for_all=allow_none_for_all)

        if len(models) != 1:
            raise ValueError(
                f"More than result for find query with argument '{what}'"
            )

        return models[0]

    def all_() -> list[_TInDbModel]:
        return find({})

    def delete_all() -> None:
        get_collection().drop()

    def delete_by_id(id_: str) -> None:
        collection = get_collection()

        collection.delete_one({"_id": ObjectId(id_)})

    def delete(model: _TInDbModel) -> None:
        return delete_by_id(model)

    def update(
            updated_model: _TInDbModel,
            *,
            post_rollback: Iterable[Callable[[], Any]] | Callable[[], Any] | None,
    ) -> _TInDbModel:
        if post_rollback is None:
            raise NotImplementedError("post_rollback argument is not supported")

        delete(updated_model)
        insert(updated_model)

        return updated_model

    def update_and_return_all(
            updated_model: _TInDbModel,
            post_rollback: Callable[[], Any] | None = None,
    ) -> list[_TInDbModel]:
        delete(updated_model)

        return all_()

    cache.prepopulate()

    base_repo = BaseRepository(
        insert=insert,
        find=find,
        first=first,
        exactly_one=exactly_one,
        all=all_,
        update=update,
        update_and_return_all=update_and_return_all,
        delete=delete,
        delete_all=delete_all,
        delete_by_id=delete_by_id,
        get_collection=get_collection,
    )

    return repo_cls(
        **dataclasses.asdict(base_repo),
        **{
            method.__name__: method for method in create_extra_methods(base_repo)
        }
    )
