import sys
import asyncio
from typing import List

import yaml
from yaml.scanner import ScannerError

from monitor.proxy import Proxy
import monitor.tasks as tasks

available_sites = {"snipes": tasks.Snipes}


class Monitor:
    def __init__(self, proxy_file: str = "proxies.txt", monitors_file: str = "monitors.yml"):
        self.proxies: List[Proxy] = []

        self._initiate_proxies(proxy_file)
        self._validate_monitor_file(monitors_file)

    def _initiate_proxies(self, proxy_file: str) -> None:
        try:
            with open(proxy_file, "r") as f:
                proxies_loaded = 0
                for line in f.readlines():
                    ip, port, username, password = line.split(":")
                    try:
                        self.proxies.append(Proxy(ip, port, username, password))
                        proxies_loaded += 1
                    except ValueError:
                        print(f"Unable to load proxy: {line}")
            print(f"{proxies_loaded} proxies have been loaded")
        except FileNotFoundError:
            print("Proxies files not found, continuing with localhost")

    def _validate_monitor_file(self, monitor_file: str) -> None:
        try:
            with open(monitor_file, "r") as f:
                try:
                    monitors: dict = yaml.safe_load(f)
                except ScannerError:
                    print("There is an error in the monitor file, please check teh format")
                    sys.exit
        except FileNotFoundError:
            print("Monitor file not found, this file is required")
            sys.exit()

        print("The following will be monitored:")
        for site, data in monitors.items():
            print(f"{site}:")
            for item in data["items"]:
                print(f"  - {item}")

    def run(self):
        pass
