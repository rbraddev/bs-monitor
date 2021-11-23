import socket
import time
from ipaddress import ip_address
from typing import Union

import httpx


class Proxy:
    def __init__(self, server: str, port: int, username: str, password: str) -> None:
        self.ip = None
        self.hostname = None
        self.port = None
        self.username = username
        self.password = password

        if None in [server, port, username, password]:
            raise ValueError("Server, port, username and password is required when creating a proxy object")

        if not self.__check_ip(server) and not self.__resolve_hostname(server):
            raise ValueError(f"Error adding proxy - {server} is not a valid IP address/hostname")

        if not self.__check_port(port):
            raise ValueError(f"Invalid port for server: {server}:{port}")

    def check_live(self) -> bool:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        return sock.connect_ex((self.ip, self.port)) == 0

    def check_response_time(self) -> Union[int, float]:
        if self.check_live():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            start = time.perf_counter()
            sock.connect_ex((self.ip, self.port))
            return round((time.perf_counter() - start) * 1000, 2)
        else:
            return -1

    def check_working(self, test_site: str = "https://www.google.com/"):
        proxies = {"all://": f"http://{self.username}:{self.password}@{self.ip}:{self.port}"}
        with httpx.Client(proxies=proxies) as client:
            try:
                start = time.perf_counter()
                res = client.get(test_site)
                response_time = round((time.perf_counter() - start) * 1000, 2)
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ProxyError):
                return {"working": False, "response_time": None}
        return {"working": res.status_code == 200, "response_time": response_time}

    async def acheck_working(self, test_site: str = "https://www.google.com/"):
        proxies = {"all://": f"http://{self.username}:{self.password}@{self.ip}:{self.port}"}
        async with httpx.AsyncClient(proxies=proxies) as client:
            try:
                start = time.perf_counter()
                res = await client.get(test_site)
                response_time = round((time.perf_counter() - start) * 1000, 2)
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ProxyError):
                return {"working": False, "response_time": None}
        return {"working": res.status_code == 200, "response_time": response_time}

    def __check_ip(self, val: str) -> bool:
        try:
            ip_address(val)
            self.ip = val
        except ValueError:
            return False
        return True

    def __resolve_hostname(self, val: str) -> bool:
        try:
            self.hostname = val
            self.ip = socket.gethostbyname(val)
        except socket.error:
            return False
        return True

    def __check_port(self, val: int) -> bool:
        try:
            val_int = int(val)
            if val_int < 1 or val_int > 65535:
                return False
            self.port = val_int
        except ValueError:
            return False
        return True

    def __repr__(self) -> str:
        return f"<Proxy {self.username}:{self.password}@{self.ip}:{self.port}>"
