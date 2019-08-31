from pymongo.cursor import Cursor
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from unittest.mock import MagicMock

from tests.utils import AsyncMock


class MongoDBCollectionMock(MagicMock):
    name = "collection"
    codec_options = None
    read_concern = None

    def __init__(self):
        super().__init__()
        self.insert_one = AsyncMock(
            return_value=InsertOneResult(inserted_id=1, acknowledged=True)
        )
        self.find = AsyncMock(
            return_value=Cursor(collection=self)
        )
        self.count_documents = AsyncMock(return_value=1)
        self.delete_many = AsyncMock(
            return_value=DeleteResult(raw_result={}, acknowledged=True)
        )
        self.update_one = AsyncMock(
            return_value=UpdateResult(raw_result={}, acknowledged=True)
        )
        self.find_one = AsyncMock(return_value={"id": 1})


class MongoDBMock(MagicMock):
    collection = MongoDBCollectionMock()
