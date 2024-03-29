import asyncio
import sys
from typing import List, Union
import random

import aiofiles
import yaml
from yaml.scanner import ScannerError

import monitor.tasks as tasks
from monitor.proxy import Proxy

available_sites = {"snipes": tasks.Snipes, "johnlewis": tasks.JohnLewis, "asda": tasks.Asda}


class Monitor:
    def __init__(self, proxy_file: str = "proxies.txt", monitors_file: str = "monitors.yml", max_workers: int = 10):
        self.proxies: List[Proxy] = []
        self.q: asyncio.Queue = None
        self.monitor_file: str = ""
        self.monitor_items: list = []
        self.max_workers: int = max_workers

        self._initiate_proxies(proxy_file)
        self._validate_monitor_file(monitors_file)

    def _initiate_proxies(self, proxy_file: str) -> None:
        try:
            with open(proxy_file, "r") as f:
                proxies_loaded = 0
                for line in f.readlines():
                    server, port, username, password = line.strip("\n").split(":")
                    try:
                        self.proxies.append(Proxy(server, port, username, password))
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
                    print("There is an error in the monitor file, please check the format")
                    sys.exit
        except FileNotFoundError:
            print("Monitor file not found, this file is required")
            sys.exit()

        self.monitor_file = monitor_file
        print("The following will be monitored:")
        for site, data in monitors.items():
            print(f"{site}:")
            for item in data["items"]:
                print(f"  - {item['title']}")

    async def _update_monitor_list(self):
        while True:
            monitors = await self._get_monitors()
            if monitors is not None:
                new_monitor_items = []
                for monitor, data in monitors.items():
                    for item in data["items"]:
                        new_monitor_items.append(
                            {
                                "site": monitor,
                                "webhook": data["webhook"],
                                "title": item["title"],
                                "product": item["product"],
                                "delay": data.get("delay", 1),
                            }
                        )

                # print(monitors)
                orig_monitor_items, self.monitor_items = self.monitor_items, new_monitor_items
                for monitor in self.monitor_items:
                    if monitor not in orig_monitor_items:
                        monitor_obj = available_sites.get(monitor["site"])
                        if monitor_obj:
                            await self.q.put(
                                monitor_obj(
                                    site=monitor["site"],
                                    webhook=monitor["webhook"],
                                    title=monitor["title"],
                                    product=monitor["product"],
                                    delay=monitor["delay"],
                                    proxies=self.proxies if self.proxies else None,
                                )
                            )
                            await asyncio.sleep(1)
            await asyncio.sleep(15)

    async def _get_monitors(self) -> Union[dict, None]:
        try:
            async with aiofiles.open(self.monitor_file) as f:
                try:
                    monitors = await f.read()
                    monitors = yaml.safe_load(monitors)
                    return monitors
                except ScannerError:
                    print("There is an error in the monitor file, continuting with the currently loaded monitor list.")
        except FileNotFoundError:
            print("Monitor file is missing, continuing with current loaded monitor list")
        return None

    async def _worker(self):
        while True:
            monitor = await self.q.get()
            await monitor.monitor()
            self.q.task_done()
            await asyncio.sleep(random.randrange(monitor.delay) or random.randrange(10))
            if monitor.__dict__() in self.monitor_items:
                await self.q.put(monitor)
            else:
                await monitor.client.aclose()

    async def _check_proxies(self):
        proxies_removed = 0
        for proxy in self.proxies:
            result = await proxy.acheck_working()
            if not result["working"]:
                self.proxies.remove(proxy)
                proxies_removed += 1
        return proxies_removed

    async def _start_tasks(self, validate_proxies: bool = False):
        if self.proxies and validate_proxies:
            print("Validating Proxies...")
            result = await self._check_proxies()
            if result > 0:
                print(f"{result} proxies removed")
        self.q = asyncio.Queue()

        await asyncio.gather(
            asyncio.create_task(self._update_monitor_list()),
            *[
                asyncio.create_task(self._worker())
                for _ in range(self.max_workers)
            ]
        )
        await self.q.join()

    def run(self, validate_proxies: bool = False):
        try:
            asyncio.run(self._start_tasks(validate_proxies))
        except KeyboardInterrupt:
            print("Monitor exited")
