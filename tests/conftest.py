"""Tests never reach the network. The owner, 2026-10-30: "do not query live bibliography
services as part of a test. that's rude and bad architecture. and it could get us locked out".

Any test that opens a connection fails here. The guard is session-scoped so that it is in place before any
module-scoped fixture runs.
"""

from __future__ import annotations

import socket
from collections.abc import Iterator

import pytest


class NetworkBlocked(RuntimeError):
    pass


@pytest.fixture(autouse=True, scope="session")
def _no_network() -> Iterator[None]:
    def refuse(*args: object, **kwargs: object) -> None:
        raise NetworkBlocked("a test tried to open a network connection (tests/conftest.py)")

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(socket.socket, "connect", refuse)
        mp.setattr(socket.socket, "connect_ex", refuse)
        mp.setattr(socket, "create_connection", refuse)
        yield
