Cookiecutter FastAPI
====================

This template generator creates a FastAPI application for a REST API.

Features
--------

* Python 3.9+ (configurable)
* Poetry_ based dependency management
* FastAPI_
* Correct `ASGI Lifespan`_ events management for FastAPI
* Session management, login/logout
* Cache using Redis (aioredis)
* Postgres asynchronous database access based on `Encode Databases`_
* Docker image for deployment based on multi-stage builds
* Development tasks registered in a ``Makefile`` for easy access and management
* Mercurial/Git hooks for ``pre-commit`` and ``pre-push`` events
* Linting based on flake8_ (and plugins), blue_, mypy_ and isort_
* Asynchronous tests based on httpx_ and alt-pytest-asyncio_


Instructions
============

You must have cookiecutter_ installed::

    $ pip install --user cookiecutter


Usage
=====

You can use this template directly from its repository::

    $ cookiecutter https://github.com/andredias/cookiecutter-fastapi.git


You will be prompted to enter a bunch of project config values.
Then,
Cookiecutter will generate a project from the template,
using the values that you entered.

That's it!


Similar Projects
================

There are a few `templates and generators for FastAPI projects`_.
All of them have their own opinionated group of implementation choices.
Since I couldn't find any who met my needs or design preferences,
I decided to create one of my own.


.. _alt-pytest-asyncio: https://pypi.org/project/alt-pytest-asyncio/
.. _ASGI Lifespan: https://pypi.org/project/asgi-lifespan/
.. _blue: https://pypi.org/project/blue/
.. _cookiecutter: https://github.com/cookiecutter/cookiecutter
.. _Encode Databases: https://www.encode.io/databases/
.. _FastAPI: https://fastapi.tiangolo.com/
.. _flake8: https://pypi.org/project/flake8/
.. _httpx: https://www.python-httpx.org/
.. _isort: https://pypi.org/project/isort/
.. _mypy: http://mypy-lang.org/
.. _Poetry: https://python-poetry.org/
.. _templates and generators for FastAPI projects: https://github.com/mjhea0/awesome-fastapi#boilerplate
