=======
History
=======

0.2.5
--------

Bugfix:

* Added sentinel value to allow None values in "id" field to be passed to Model internal methods

0.2.4
--------

General changes:

* Added support for latest FastAPI & Pydantic (fastapi==0.52.0, pydantic==1.4)

Breaking changes:

* Due to the breaking changes between pydantic < 1.0 and pydantic > 1.0 this version will only work with the latter.

0.2.0
--------

General changes:

* Added support for Python 3.8

Breaking changes:

* Changed the way of how the error structure look like

.. code-block:: json

    [
        {
            "error_codes": [400, 401],
            "message": "Validation error.",
            "fields": [
                {
                    "name": "field1",
                    "message": "Field is required",
                    "error_code": 400
                },
                {
                    "name": "field2",
                    "message": "Invalid value",
                    "error_code": 401
                }
            ]
        }
    ]
