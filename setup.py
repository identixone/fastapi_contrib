#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

requirements = [
    'fastapi>=0.63.0'
]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    author="Lev Rubel",
    author_email="l@datacorp.ee",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="Opinionated set of utilities on top of FastAPI",
    install_requires=requirements,
    extras_require={
        "mongo": ["motor>=2.0.0"],
        "ujson": ["ujson<2.0.0"],
        "pytz": ["pytz"],
        "jaegertracing": ["jaeger-client>=4.1.0", "opentracing>=2.2.0"],
        "all": [
            "motor>=2.0.0",
            "ujson<2.0.0",
            "pytz",
            "jaeger-client>=4.1.0",
            "opentracing>=2.2.0",
        ],
    },
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords="fastapi_contrib",
    name="fastapi_contrib",
    packages=find_packages(exclude=["tests", "tests.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/identixone/fastapi_contrib",
    version="0.2.10",
    zip_safe=False,
)
