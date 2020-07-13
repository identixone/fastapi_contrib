import contextvars
import warnings

from typing import Any

from opentracing import tags
from opentracing.propagation import Format

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


request_span = contextvars.ContextVar('request_span')


class OpentracingMiddleware(BaseHTTPMiddleware):

    @staticmethod
    def before_request(request: Request, tracer):
        """
        Gather various info about the request and start new span with the data.
        """
        span_context = tracer.extract(
            format=Format.HTTP_HEADERS, carrier=request.headers
        )
        span = tracer.start_span(
            operation_name=f"{request.method} {request.url.path}",
            child_of=span_context,
        )
        span.set_tag("http.url", str(request.url))

        remote_ip = request.client.host
        span.set_tag(tags.PEER_HOST_IPV4, remote_ip or "")

        remote_port = request.client.port
        span.set_tag(tags.PEER_PORT, remote_port or "")

        return span

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """
        Store span in some request.state storage using Tracer.scope_manager,
        using the returned `Scope` as Context Manager to ensure
        `Span` will be cleared and (in this case) `Span.finish()` be called.

        :param request: Starlette's Request object
        :param call_next: Next callable Middleware in chain or final view
        :return: Starlette's Response object
        """
        tracer = request.app.state.tracer
        span = self.before_request(request, tracer)

        with tracer.scope_manager.activate(span, True) as scope:
            request_span.set(span)

            warnings.warn(
                """
                opentracing objects request.state will be removed in favor of
                saving them in request's scope in the next minor version 0.3.0
                """,
                FutureWarning
            )

            request.state.opentracing_span = span
            request.scope["opentracing_span"] = span
            request.state.opentracing_scope = scope
            request.scope["opentracing_scope"] = scope
            request.state.opentracing_tracer = tracer
            request.scope["opentracing_tracer"] = tracer
            response = await call_next(request)
        return response
