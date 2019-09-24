from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from unittest.mock import MagicMock

from tests.utils import AsyncMock, AsyncIterator


class MongoDBCollectionMock(MagicMock):
    name = "collection"
    codec_options = None
    read_concern = None

    def __init__(self, collection_name, **kwargs):
        super().__init__()
        self.name = collection_name
        find_one_result = kwargs.get("find_one_result", {"_id": 1})
        inserted_id = kwargs.get("inserted_id", 1)
        create_indexes_result = kwargs.get("create_indexes_result", None)

        self.insert_one = AsyncMock(
            return_value=InsertOneResult(
                inserted_id=inserted_id, acknowledged=True
            )
        )
        self.delete_many = AsyncMock(
            return_value=DeleteResult(raw_result={}, acknowledged=True)
        )
        self.update_one = AsyncMock(
            return_value=UpdateResult(raw_result={}, acknowledged=True)
        )
        self.update_many = AsyncMock(
            return_value=UpdateResult(raw_result={}, acknowledged=True)
        )
        self.count_documents = AsyncMock(return_value=1)
        self.find_one = AsyncMock(return_value=find_one_result)
        self.create_indexes = AsyncMock(return_value=create_indexes_result)

    def find(self, *args, **kwargs):
        return AsyncIterator([{"_id": 1}])


class MongoDBMock(MagicMock):
    def __init__(self, collection_name="collection", **kwargs):
        super().__init__()
        collection_mock = MongoDBCollectionMock(
            collection_name=collection_name, **kwargs
        )
        self.get_collection = MagicMock(return_value=collection_mock)
