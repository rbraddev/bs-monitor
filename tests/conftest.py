import pytest

from monitor.proxy import Proxy


@pytest.fixture
def proxy():
    with open("test_proxy.txt", "r") as f:
        ip, port, username, password = f.readline().split(":")
    return Proxy(ip, int(port), username, password)


@pytest.fixture
def proxy_fail():
    return Proxy("2.0.0.0", 443, "fakeuser", "fakepass")
