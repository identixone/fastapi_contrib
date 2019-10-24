.. highlight:: shell

============
Installation
============


Stable release
--------------

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


This is the preferred method to install FastAPI Contrib, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for FastAPI Contrib can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/l@datacorp.ee/fastapi_contrib

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/l@datacorp.ee/fastapi_contrib/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/l@datacorp.ee/fastapi_contrib
.. _tarball: https://github.com/l@datacorp.ee/fastapi_contrib/tarball/master
