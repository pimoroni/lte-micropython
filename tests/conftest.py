import sys
import time
from collections import deque
from unittest import mock

import pytest


class Clock:
    """A fake monotonic clock, so timeouts fire without real delay."""

    def __init__(self):
        self.ms = 0
        self.sleeps = []

    def advance(self, ms):
        self.ms += ms


class FakeUART:
    """A UART stand-in that replays scripted AT responses.

    `responses` maps a written command (stripped) to the byte lines the module
    would send back. Any readline with nothing queued advances the clock, so a
    read that never terminates hits its timeout immediately.
    """

    def __init__(self, clock, responses=None):
        self._clock = clock
        self.responses = responses or {}
        self.written = []
        self._rx = deque()

    def init(self, **kwargs):
        pass

    def write(self, data):
        self.written.append(data)
        if isinstance(data, str):
            for line in self.responses.get(data.strip(), []):
                self._rx.append(line if isinstance(line, bytes) else line.encode("ascii"))

    def flush(self):
        pass

    def any(self):
        return sum(len(line) for line in self._rx)

    def read(self, length=None):
        data = b"".join(self._rx)
        self._rx.clear()
        return data

    def readline(self):
        if self._rx:
            return self._rx.popleft()
        self._clock.advance(100)
        return None


class FakePin:
    def __init__(self):
        self.values = []

    def value(self, level):
        self.values.append(level)


@pytest.fixture(scope="function", autouse=True)
def micropython():
    sys.modules["micropython"] = mock.MagicMock()
    sys.modules["micropython"].const = lambda x: x
    yield sys.modules["micropython"]
    del sys.modules["micropython"]


@pytest.fixture(scope="function", autouse=True)
def machine():
    sys.modules["machine"] = mock.MagicMock()
    yield sys.modules["machine"]
    del sys.modules["machine"]


@pytest.fixture(scope="function", autouse=True)
def network():
    sys.modules["network"] = mock.MagicMock()
    yield sys.modules["network"]
    del sys.modules["network"]


@pytest.fixture(scope="function", autouse=True)
def clock(monkeypatch):
    """Drive time.* off a fake clock. Sleeps advance it and are recorded."""
    c = Clock()

    def _sleep(seconds):
        c.sleeps.append(seconds)
        c.advance(int(seconds * 1000))

    monkeypatch.setattr(time, "ticks_ms", lambda: c.ms, raising=False)
    monkeypatch.setattr(time, "ticks_add", lambda ticks, delta: ticks + delta, raising=False)
    monkeypatch.setattr(time, "ticks_diff", lambda a, b: a - b, raising=False)
    monkeypatch.setattr(time, "time", lambda: c.ms / 1000.0)
    monkeypatch.setattr(time, "sleep", _sleep)
    return c


@pytest.fixture
def uart(clock):
    return FakeUART(clock)


@pytest.fixture
def reset_pin():
    return FakePin()
