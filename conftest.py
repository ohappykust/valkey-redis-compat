"""Session-scoped fixtures shared across all tests."""

import pytest
import valkey


@pytest.fixture(scope="session")
def _valkey_reachable():
    """Check once per session if Valkey is reachable on localhost:6379."""
    try:
        c = valkey.Valkey(host="localhost", port=6379, db=15, socket_timeout=1)
        c.ping()
        c.close()
        return True
    except Exception:
        return False
