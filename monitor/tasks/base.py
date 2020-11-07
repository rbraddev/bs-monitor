import json

import httpx

from monitor.proxy import Proxy


class Task:
    def __init__(self, site, webhook: str, title: str, item: str, delay: int = 1, proxy: Proxy = None):
        if self.site not in site:
            raise ValueError(f"{site} is invalid for this task")

        self.webhook: str = webhook
        self.title: str = title
        self.item: str = item
        self.delay: int = delay
        self.proxy: Proxy = proxy
        self.stock: dict = {}
        self.client: httpx.AsyncClient = None

    async def monitor(self):
        if self.client is None:
            proxies = None
            if self.proxy:
                proxies = {
                    "all://": f"http://{self.proxy.username}:{self.proxy.password}@{self.proxy.ip}:{self.proxy.port}"
                }
            self.client = httpx.AsyncClient(proxies=proxies)

        print(f"ITEM: {self.item}")
        try:
            response = await self.client.get(url=self.item)
            if response.status_code == 200:
                await self.check_product(response.text)
            else:
                print(f"Monitor: {self.item}, Status code: {response.status_code}")
        except httpx.ConnectError:
            print(f"Connection error for monitor: {self.item}")

    async def _send_webhook(self, data):
        headers = {"content-type": "application/json"}
        nl = "\n"
        payload = {
            "content": "In Stock",
            "username": "bs-monitor",
            "embeds": [
                {
                    "title": self.site.capitalize(),
                    "description": f"[{self.title}]({self.item})\n\nAvailable Sizes:\n{nl.join([k for k, v in self.stock.items() if v])}",
                }
            ],
        }
        async with httpx.AsyncClient() as client:
            await client.post(url=self.webhook, data=json.dumps(payload), headers=headers)

    async def print_test(self):
        print(f"{self.site} - {self.item} - {self.proxy.ip}")

    def __dict__(self):
        return {
            "site": self.site,
            "webhook": self.webhook,
            "title": self.title,
            "item": self.item,
            "delay": self.delay,
        }
