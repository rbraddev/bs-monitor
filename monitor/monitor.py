import asyncio
import sys
from random import randrange
from typing import List, Union

import aiofiles
import yaml
from yaml.scanner import ScannerError

import monitor.tasks as tasks
from monitor.proxy import Proxy

available_sites = {"snipes": tasks.Snipes, "asos": tasks.Asos}


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

        self.monitor_file = monitor_file
        print("The following will be monitored:")
        for site, data in monitors.items():
            print(f"{site}:")
            for item in data["items"]:
                print(f"  - {item}")

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
                                "item": item,
                                "delay": data.get("delay"),
                            }
                        )

                print(monitors)
                orig_monitor_items, self.monitor_items = self.monitor_items, new_monitor_items
                for monitor in self.monitor_items:
                    if monitor not in orig_monitor_items:
                        monitor_obj = available_sites.get(monitor["site"])
                        if monitor_obj:
                            await self.q.put(
                                monitor_obj(
                                    site=monitor["site"],
                                    webhook=monitor["webhook"],
                                    item=monitor["item"],
                                    delay=monitor["delay"],
                                    proxy=self.proxies[randrange(len(self.proxies))],
                                )
                            )
                            await asyncio.sleep(1)
            await asyncio.sleep(10)

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
            await monitor.print_test()
            self.q.task_done()
            await asyncio.sleep(monitor.delay or 1)
            if monitor.__dict__() in self.monitor_items:
                await self.q.put(monitor)

    async def _start_tasks(self):
        self.q = asyncio.Queue()
        tasks = [asyncio.create_task(self._update_monitor_list())]
        for _ in range(self.max_workers):
            asyncio.create_task(self._worker())
        await asyncio.gather(*tasks)
        await self.q.join()

    def run(self):
        try:
            asyncio.run(self._start_tasks())
        except KeyboardInterrupt:
            print("Monitor exited")
