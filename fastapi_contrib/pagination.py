import asyncio

from starlette.requests import Request

from fastapi_contrib.serializers.common import Serializer


class Pagination(object):
    def __init__(self, request: Request, offset: int = 0, limit: int = 100):
        """
        Query params parser and db collection paginator in one.
        :param request: starlette Request object
        :param offset: query param of how many records to skip
        :param limit: query param of how many records to show
        """
        self.request = request
        self.offset = offset
        self.limit = limit
        self.model = None
        self.count = None
        self.list = []

    async def get_count(self, **kwargs) -> int:
        self.count = await self.model.count(**kwargs)
        return self.count

    def get_next_url(self) -> str:
        if self.offset + self.limit >= self.count:
            return None
        return str(
            self.request.url.replace_query_params(
                limit=self.limit, offset=self.offset + self.limit
            )
        )

    def get_previous_url(self) -> str:
        if self.offset <= 0:
            return None

        if self.offset - self.limit <= 0:
            return str(self.request.url.remove_query_params(keys=["offset"]))

        return str(
            self.request.url.replace_query_params(
                limit=self.limit, offset=self.offset - self.limit
            )
        )

    async def get_list(self, **kwargs) -> list:
        self.list = await self.model.list(
            _limit=self.limit, _offset=self.offset, raw=True, **kwargs
        )
        return self.list

    async def paginate(self, serializer_class: Serializer, **kwargs) -> dict:
        self.model = serializer_class.Meta.model
        count, _list = await asyncio.gather(
            self.get_count(**kwargs), self.get_list(**kwargs)
        )
        # TODO: think about naming and separation of concerns
        _list = serializer_class.sanitize_list(_list)
        return {
            "count": count,
            "next": self.get_next_url(),
            "previous": self.get_previous_url(),
            "result": _list,
        }
