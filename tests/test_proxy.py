import pytest

from monitor.proxy import Proxy


@pytest.mark.parametrize(
    "server, port, username, password, obj",
    [
        [
            "12.12.12.12",
            2000,
            "fakeuser",
            "fakepass",
            {"ip": "12.12.12.12", "hostname": None, "port": 2000, "username": "fakeuser", "password": "fakepass"},
        ],
        [
            "12.12.12.12",
            "2000",
            "fakeuser",
            "fakepass",
            {"ip": "12.12.12.12", "hostname": None, "port": 2000, "username": "fakeuser", "password": "fakepass"},
        ],
        [
            "one.one.one.one",
            2000,
            "fakeuser",
            "fakepass",
            {
                "ip": "1.1.1.1",
                "hostname": "one.one.one.one",
                "port": 2000,
                "username": "fakeuser",
                "password": "fakepass",
            },
        ],
    ],
)
def test_successful_proxy_obj(server, port, username, password, obj):
    proxy = Proxy(server, port, username, password)
    assert proxy.ip == obj["ip"] or "1.0.0.1"
    assert proxy.hostname == obj["hostname"]
    assert proxy.port == obj["port"]
    assert proxy.username == obj["username"]
    assert proxy.password == obj["password"]


@pytest.mark.parametrize(
    "server, port, username, password",
    [
        ["12.12.12.12", 2000000, "fakeuser", "fakepass"],
        ["12.12.12.12", "200000000", "fakeuser", "fakepass"],
        ["12.12.12.12", "noport", "fakeuser", "fakepass"],
        ["12.12.12.12", None, "fakeuser", "fakepass"],
        ["12.12.12.12", -1, "fakeuser", "fakepass"],
        ["12.12.12.12", "0", "fakeuser", "fakepass"],
    ],
)
def test_invalid_port(server, port, username, password):
    with pytest.raises(ValueError):
        Proxy(server, port, username, password)


@pytest.mark.parametrize(
    "server, port, username, password",
    [
        [None, 2000, "fakeuser", "fakepass"],
        ["12.12.12.12.12", 2000, "fakeuser", "fakepass"],
        ["a.fake.domain", 2000, "fakeuser", "fakepass"],
    ],
)
def test_invalid_server(server, port, username, password):
    with pytest.raises(ValueError):
        Proxy(server, port, username, password)


def test_check_live_pass(proxy):
    assert proxy.check_live()


def test_check_live_fail(proxy_fail):
    assert not proxy_fail.check_live()


def test_check_working_pass(proxy):
    result = proxy.check_working()
    assert result["working"]
    assert isinstance(result["response_time"], float)


def test_check_working_fail(proxy_fail):
    result = proxy_fail.check_working()
    assert not result["working"]
    assert not result["response_time"]


def test_check_response_time_pass(proxy):
    assert isinstance(proxy.check_response_time(), float)


def test_check_response_time_failproxy(proxy_fail):
    assert proxy_fail.check_response_time() == -1
