===============
FastAPI Contrib
===============


.. image:: https://img.shields.io/pypi/v/fastapi_contrib.svg
        :target: https://pypi.python.org/pypi/fastapi_contrib

.. image:: https://img.shields.io/travis/identixone/fastapi_contrib.svg
        :target: https://travis-ci.org/identixone/fastapi_contrib

.. image:: https://readthedocs.org/projects/fastapi-contrib/badge/?version=latest
        :target: https://fastapi-contrib.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/identixone/fastapi_contrib/shield.svg
     :target: https://pyup.io/repos/github/identixone/fastapi_contrib/
     :alt: Updates



Opinionated set of utilities on top of FastAPI


* Free software: MIT license
* Documentation: https://fastapi-contrib.readthedocs.io.


Features
--------

* Auth Backend & Middleware (User or None in every request object)
* Permissions: reusable class permissions, specify multiple as FastAPI Dependency
* ModelSerializers: serialize (pydantic) incoming request, connect data with DB model and save
* UJSONResponse: correctly show slashes in fields with URLs
* Limit-Offset Pagination: use it as FastAPI Dependency (works only with ModelSerializers for now)
* MongoDB integration: Use models as if it was Django (based on pydantic models)
* MongoDB indices verification on startup of the app
* Custom Exceptions and Custom Exception Handlers
* Opentracing middleware & setup utility with Jaeger tracer + root span available in every Request's state
* StateRequestIDMiddleware: receives configurable header and saves it in request state

Roadmap
--------

See GitHub Project `Roadmap <https://github.com/identixone/fastapi_contrib/projects/2>`_.

Installation
------------

To install just Contrib (without mongodb, pytz, ujson):

.. code-block:: console

    $ pip install fastapi_contrib

To install contrib with mongodb support:

.. code-block:: console

    $ pip install fastapi_contrib[mongo]

To install contrib with ujson support:

.. code-block:: console

    $ pip install fastapi_contrib[ujson]

To install contrib with pytz support:

.. code-block:: console

    $ pip install fastapi_contrib[pytz]

To install contrib with opentracing & Jaeger tracer:

.. code-block:: console

    $ pip install fastapi_contrib[jaegertracing]

To install everything:

.. code-block:: console

    $ pip install fastapi_contrib[all]

Usage
-----

To use Limit-Offset pagination:

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_contrib.pagination import Pagination
    from fastapi_contrib.serializers.common import ModelSerializer
    from yourapp.models import SomeModel

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

Subclass this pagination to define custom default & maximum values for offset & limit:

.. code-block:: python

    class CustomPagination(Pagination):
        default_offset = 90
        default_limit = 1
        max_offset = 100
        max_limit = 2000


To use State Request ID Middleware:

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_contrib.common.middlewares import StateRequestIDMiddleware

    app = FastAPI()

    @app.on_event('startup')
    async def startup():
        app.add_middleware(StateRequestIDMiddleware)


To use Authentication Middleware:

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_contrib.auth.backends import AuthBackend
    from fastapi_contrib.auth.middlewares import AuthenticationMiddleware

    app = FastAPI()

    @app.on_event('startup')
    async def startup():
        app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())


Define & use custom permissions based on FastAPI Dependency framework:

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_contrib.permissions import BasePermission, PermissionsDependency

    class TeapotUserAgentPermission(BasePermission):

        def has_required_permissions(self, request: Request) -> bool:
            return request.headers.get('User-Agent') == "Teapot v1.0"

    app = FastAPI()

    @app.get(
        "/teapot/",
        dependencies=[Depends(
            PermissionsDependency([TeapotUserAgentPermission]))]
    )
    async def teapot() -> dict:
        return {"teapot": True}


Setup uniform exception-handling:

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_contrib.exception_handlers import setup_exception_handlers

    app = FastAPI()

    @app.on_event('startup')
    async def startup():
        setup_exception_handlers(app)


If you want to correctly handle scenario when request is an empty body (IMPORTANT: non-multipart):

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_contrib.routes import ValidationErrorLoggingRoute

    app = FastAPI()
    app.router.route_class = ValidationErrorLoggingRoute


Or if you use multiple routes for handling different namespaces (IMPORTANT: non-multipart):

.. code-block:: python

    from fastapi import APIRouter, FastAPI
    from fastapi_contrib.routes import ValidationErrorLoggingRoute

    app = FastAPI()

    my_router = APIRouter(route_class=ValidationErrorLoggingRoute)


To correctly show slashes in fields with URLs + ascii locking:

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_contrib.common.responses import UJSONResponse

    app = FastAPI()

    @app.get("/", response_class=UJSONResponse)
    async def root():
        return {"a": "b"}


Or specify it as default response class for the whole app (FastAPI >= 0.39.0):

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_contrib.common.responses import UJSONResponse

    app = FastAPI(default_response_class=UJSONResponse)


To setup Jaeger tracer and enable Middleware that captures every request in opentracing span:

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_contrib.tracing.middlewares import OpentracingMiddleware
    from fastapi_contrib.tracing.utils import setup_opentracing

    app = FastAPI()

    @app.on_event('startup')
    async def startup():
        setup_opentracing(app)
        app.add_middleware(OpentracingMiddleware)



To setup mongodb connection at startup and never worry about it again:

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_contrib.db.utils import setup_mongodb

    app = FastAPI()

    @app.on_event('startup')
    async def startup():
        setup_mongodb(app)


Use models to map data to MongoDB:

.. code-block:: python

    from fastapi_contrib.db.models import MongoDBModel

    class MyModel(MongoDBModel):
        additional_field1: str
        optional_field2: int = 42

        class Meta:
            collection = "mymodel_collection"


    mymodel = MyModel(additional_field1="value")
    mymodel.save()

    assert mymodel.additional_field1 == "value"
    assert mymodel.optional_field2 == 42
    assert isinstance(mymodel.id, int)


Or use TimeStamped model with creation datetime:

.. code-block:: python

    from fastapi_contrib.db.models import MongoDBTimeStampedModel

    class MyTimeStampedModel(MongoDBTimeStampedModel):

        class Meta:
            collection = "timestamped_collection"


    mymodel = MyTimeStampedModel()
    mymodel.save()

    assert isinstance(mymodel.id, int)
    assert isinstance(mymodel.created, datetime)


Use serializers and their response models to correctly show Schemas and convert from JSON/dict to models and back:

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_contrib.db.models import MongoDBModel
    from fastapi_contrib.serializers import openapi
    from fastapi_contrib.serializers.common import Serializer

    from yourapp.models import SomeModel

    app = FastAPI()


    class SomeModel(MongoDBModel):
        field1: str


    @openapi.patch
    class SomeSerializer(Serializer):
        read_only1: str = "const"
        write_only2: int
        not_visible: str = "42"

        class Meta:
            model = SomeModel
            exclude = {"not_visible"}
            write_only_fields = {"write_only2"}
            read_only_fields = {"read_only1"}


    @app.get("/", response_model=SomeSerializer.response_model)
    async def root(serializer: SomeSerializer):
        model_instance = await serializer.save()
        return model_instance.dict()


POST-ing to this route following JSON:

.. code-block:: json

    {"read_only1": "a", "write_only2": 123, "field1": "b"}


Should return following response:

.. code-block:: json

    {"id": 1, "field1": "b", "read_only1": "const"}


Auto-creation of MongoDB indexes
----------------------------------------------------------------

Suppose we have this directory structure:

.. code-block:: console

    -- project_root/
         -- apps/
              -- app1/
                   -- models.py (with MongoDBModel inside with indices declared)
              -- app2/
                   -- models.py (with MongoDBModel inside with indices declared)

Based on this, your name of the folder with all the apps would be "apps". This is the default name for fastapi_contrib package to pick up your structure automatically. You can change that by setting ENV variable `CONTRIB_APPS_FOLDER_NAME` (by the way, all the setting of this package are overridable via ENV vars with `CONTRIB_` prefix before them).

You also need to tell fastapi_contrib which apps to look into for your models. This is controlled by `CONTRIB_APPS` ENV variable, which is list of str names of the apps with models. In the example above, this would be `CONTRIB_APPS=["app1","app2"]`.

Just use create_indexes function after setting up mongodb:

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_contrib.db.utils import setup_mongodb, create_indexes

    app = FastAPI()

    @app.on_event("startup")
    async def startup():
        setup_mongodb(app)
        await create_indexes()


This will scan all the specified `CONTRIB_APPS` in the `CONTRIB_APPS_FOLDER_NAME` for models, that are subclassed from either MongoDBModel or MongoDBTimeStampedModel and create indices for any of them that has Meta class with indexes attribute:

models.py:

.. code-block:: python

    import pymongo
    from fastapi_contrib.db.models import MongoDBTimeStampedModel


    class MyModel(MongoDBTimeStampedModel):

        class Meta:
            collection = "mymodel"
            indexes = [
                pymongo.IndexModel(...),
                pymongo.IndexModel(...),
            ]


This would not create duplicate indices because it relies on pymongo and motor to do all the job.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
