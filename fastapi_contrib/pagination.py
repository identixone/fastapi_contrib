import asyncio

from starlette.requests import Request

from fastapi_contrib.serializers.common import Serializer


class Pagination(object):
    """
    Query params parser and db collection paginator in one.

    Use it as dependency in route, then invoke `paginate` with serializer:

    .. code-block:: python

        app = FastAPI()

        class SomeSerializer(ModelSerializer):
            class Meta:
                model = SomeModel

        @app.get("/")
        async def list(pagination: Pagination = Depends()):
            filter_kwargs = {}
            return await pagination.paginate(
                serializer_class=SomeSerializer, **filter_kwargs
            )

    :param request: starlette Request object
    :param offset: query param of how many records to skip
    :param limit: query param of how many records to show
    """

    def __init__(self, request: Request, offset: int = 0, limit: int = 100):
        self.request = request
        self.offset = offset
        self.limit = limit
        self.model = None
        self.count = None
        self.list = []

    async def get_count(self, **kwargs) -> int:
        """
        Retrieves counts for query list, filtered by kwargs.

        :param kwargs: filters that are proxied in db query
        :return: number of found records
        """
        self.count = await self.model.count(**kwargs)
        return self.count

    def get_next_url(self) -> str:
        """
        Constructs `next` parameter in resulting JSON,
        produces URL for next "page" of paginated results.

        :return: URL for next "page" of paginated results.
        """
        if self.offset + self.limit >= self.count:
            return None
        return str(
            self.request.url.replace_query_params(
                limit=self.limit, offset=self.offset + self.limit
            )
        )

    def get_previous_url(self) -> str:
        """
        Constructs `previous` parameter in resulting JSON,
        produces URL for previous "page" of paginated results.

        :return: URL for previous "page" of paginated results.
        """
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
        """
        Retrieves actual list of records. It comes raw, which means
        it retrieves dict from DB, instead of making conversion
        for every object in list into Model.

        :param kwargs: filters that are proxied in db query
        :return: list of dicts from DB, filtered by kwargs
        """
        self.list = await self.model.list(
            _limit=self.limit, _offset=self.offset, raw=True, **kwargs
        )
        return self.list

    async def paginate(self, serializer_class: Serializer, **kwargs) -> dict:
        """
        Actual pagination function, takes serializer class,
        filter options as kwargs and returns dict with the following fields:
            * count - counts for query list, filtered by kwargs
            * next - URL for next "page" of paginated results
            * previous - URL for previous "page" of paginated results
            * result - actual list of records (dicts)

        :param serializer_class: needed to get Model & sanitize list from DB
        :param kwargs: filters that are proxied in db query
        :return: dict that should be returned as a response
        """
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
