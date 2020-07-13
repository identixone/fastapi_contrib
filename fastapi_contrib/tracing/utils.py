import warnings

from jaeger_client import Config
from opentracing.scope_managers.asyncio import AsyncioScopeManager

from fastapi_contrib.conf import settings


def setup_opentracing(app):
    """
    Helper function to setup opentracing with Jaeger client during setup.
    Use during app startup as follows:

    .. code-block:: python

        app = FastAPI()

        @app.on_event('startup')
        async def startup():
            setup_opentracing(app)

    :param app: app object, instance of FastAPI
    :return: None
    """
    config = Config(
        config={
            "local_agent": {
                "reporting_host": settings.jaeger_host,
                "reporting_port": settings.jaeger_port
            },
            "sampler": {
                "type": settings.jaeger_sampler_type,
                "param": settings.jaeger_sampler_rate,
            },
            "trace_id_header": settings.trace_id_header
        },
        service_name=settings.service_name,
        validate=True,
        scope_manager=AsyncioScopeManager()
    )

    warnings.warn(
        """
        tracer object in request.app will be removed in favor of saving it in
        request.app.state in the next minor version 0.3.0
        """,
        FutureWarning
    )
    # this call also sets opentracing.tracer
    app.state.tracer = config.initialize_tracer()
    app.tracer = app.state.tracer
