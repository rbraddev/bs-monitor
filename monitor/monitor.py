import sys
import asyncio
from typing import List

import aiofile
import yaml
from yaml.scanner import ScannerError

from monitor.proxy import Proxy
import monitor.tasks as tasks

available_sites = {"snipes": tasks.Snipes}


class Monitor:
    def __init__(self, proxy_file: str = "proxies.txt", monitors_file: str = "monitors.yml", max_workers: int = 10):
        self.proxies: List[Proxy] = []
        self.q: asyncio.Queue = None
        self.monitor_list: list = []
        self.max_workers: int = max_workers

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

    async def _update_monitor(self):
        while True:
            try:
                async with aiofiles.open("test_tasks.yml") as f:
                    try:
                        monitors = await f.read()
                        monitors = yaml.safe_load(tasks)
                    except ScannerError:
                        print("There is an error in the monitor file, continuting with the currently loaded monitor list.")
            except FileNotFoundError:
                print("Monitor file is missing, continuing with current loaded monitor list")

            for monitor in monitors:
                if monitor not in self.monitor_list:
                    self.monitor_list.append(task)
                    await self.q.put(task)
            await asyncio.sleep(5)

    async def _start_tasks(self):
        self.q = asyncio.Queue()
        tasks = [asyncio.create_task(self.update_tasks())]
        for _ in range(self.max_workers):
            asyncio.create_task(self._worker())
        await asyncio.gather(*tasks)
        await self.q.join()

    def run(self):
        try:
            asyncio.run(self._start_tasks())
        except KeyboardInterrupt:
            print("Monitor exited")
