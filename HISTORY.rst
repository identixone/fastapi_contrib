=======
History
=======

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
