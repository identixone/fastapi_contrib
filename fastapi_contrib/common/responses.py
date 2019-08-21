import typing
import ujson

from starlette.responses import UJSONResponse as BaseUJSONResponse


class UJSONResponse(BaseUJSONResponse):

    def render(self, content: typing.Any) -> bytes:
        return ujson.dumps(
            content, ensure_ascii=True, escape_forward_slashes=False
        ).encode("utf-8")
