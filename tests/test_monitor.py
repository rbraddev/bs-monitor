import pytest

from monitor.monitor import Monitor
from monitor.proxy import Proxy


def test_monitor_obj_succesful():
    monitor = Monitor(proxy_file="test_proxy.txt")
    assert len(monitor.proxies) == 1
    assert isinstance(monitor.proxies[0], Proxy)
