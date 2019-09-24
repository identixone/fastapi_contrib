import logging

from unittest.mock import MagicMock


def AsyncMock(*args, **kwargs):
    m = MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


class AsyncIterator:
    def __init__(self, items):
        self.items = items

    async def __aiter__(self):
        for item in self.items:
            yield item


def override_settings(**decorator_kwargs):
    def decorator(function):
        def wrapper(*args, **kwargs):
            from fastapi_contrib.conf import settings
            for kwarg, value in decorator_kwargs.items():
                setattr(settings, kwarg, value)

            return function(*args, **kwargs)
        return wrapper
    return decorator


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs.

    Messages are available from an instance's ``messages`` dict, in order,
    indexed by a lowercase log level string (e.g., 'debug', 'info', etc.).
    """

    def __init__(self, *args, **kwargs):
        self.messages = {
            'debug': [], 'info': [], 'warning': [], 'error': [], 'critical': []
        }
        super().__init__(*args, **kwargs)

    def emit(self, record):
        """
        Store a message from ``record`` in the instance's ``messages`` dict.
        """
        try:
            self.messages[record.levelname.lower()].append(record.getMessage())
        except Exception:
            self.handleError(record)

    def reset(self):
        self.acquire()
        try:
            for message_list in self.messages.values():
                message_list.clear()
        finally:
            self.release()
