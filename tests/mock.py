from motor.motor_asyncio import AsyncIOMotorCursor
from pymongo.cursor import Cursor
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from unittest.mock import MagicMock

from tests.utils import AsyncMock


class MongoDBCollectionMock(MagicMock):
    name = "collection"
    codec_options = None
    read_concern = None

    def __init__(self, **kwargs):
        super().__init__()
        find_one_result = kwargs.get('find_one_result', {"_id": 1})
        create_indexes_result = kwargs.get('create_indexes_result', None)

        self.insert_one = AsyncMock(
            return_value=InsertOneResult(inserted_id=1, acknowledged=True)
        )
        self.delete_many = AsyncMock(
            return_value=DeleteResult(raw_result={}, acknowledged=True)
        )
        self.update_one = AsyncMock(
            return_value=UpdateResult(raw_result={}, acknowledged=True)
        )
        cursor = MagicMock()
        cursor.to_list = AsyncMock(return_value=[{"_id": 1}])
        self.find = MagicMock(return_value=cursor)
        self.count_documents = AsyncMock(return_value=1)
        self.find_one = AsyncMock(return_value=find_one_result)
        self.create_indexes = AsyncMock(return_value=create_indexes_result)


class MongoDBMock(MagicMock):

    def __init__(self, collection_name="collection", **kwargs):
        super().__init__()
        collection_mock = MongoDBCollectionMock(**kwargs)
        setattr(self, collection_name, collection_mock)
