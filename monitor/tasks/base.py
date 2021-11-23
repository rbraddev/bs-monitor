from random import randrange
from typing import *
import json

import httpx

from monitor.proxy import Proxy


class Task:
    def __init__(self, site, webhook: str, title: str, product: str, delay: int = 1, proxies: List[Proxy] = None):
        if self.site not in site:
            raise ValueError(f"{site} is invalid for this task")

        self.webhook: str = webhook
        self.errorhook: str = "https://discord.com/api/webhooks/897482578334982166/n_PKQOZc9x_54ZVAEeib_Hcl0qbMMeN8bvVVgW6b1qsDM6US6W_H7sWO7iAOqLbjuL1n"
        self.title: str = title
        self.product: str = product
        self.delay: int = delay
        self.proxies: List[Proxy] = proxies
        self.proxy: Proxy = None
        self.stock: int = 0
        self.client: httpx.AsyncClient = None

    def _init_client(self):
        proxies = {}
        if self.proxies:
            self.proxy = self.proxies[randrange(len(self.proxies))]
            proxies = {
                "all://": f"http://{self.proxy.username}:{self.proxy.password}@{self.proxy.ip}:{self.proxy.port}"
            }
        headers = {}
        if self.user_agent:
            headers.update({"User-Agent": self.user_agent})
        self.client = httpx.AsyncClient(proxies=proxies, headers=headers)

    async def monitor(self):
        self._init_client()

        print(f"{self.site} - {self.title} - {self.product}")
        try:
            async with self.client as client:
                response = await client.get(self.url, timeout=6, allow_redirects=False)
                print(response.status_code)
                await self._send_webhook(error=response.status_code)
            if response.status_code == httpx.codes.OK:
                await self.check_product(response.text)
            else:
                await self._send_webhook(error=f"Monitor: {self.product}, Status code: {response.status_code}")
        except httpx.ConnectError:
            await self._send_webhook(error=f"Connection error for monitor: {self.product}")
        except httpx.ProxyError:
            try:
                self.proxies.remove(self.proxy)
            except ValueError:
                await self._send_webhook(error="No Proxies Left!!")
            await self._send_webhook(error=f"Proxy Error: {self.proxy} - Proxies available: {len(self.proxies)}")
        except Exception as e:
            await self._send_webhook(error=f"Monitor: {self.product}, Error: {e}")

    async def _send_webhook(self, error: str = None):
        headers = {"content-type": "application/json"}
        nl = "\n"
        payload = {
            "username": "bs-monitor",
            "embeds": [
                {
                    "title": f"{self.site.capitalize()} - {self.title}",
                    "url": self.product_url,
                    "description": error if error else f"{'In stock ' + str(self.stock) + '... GO GO GO!' if self.stock > 0 else 'In Stock... GO GO GO!'}",
                }
            ],
        }
        async with httpx.AsyncClient() as client:
            await client.post(url=self.errorhook if error else self.webhook, data=json.dumps(payload), headers=headers)

    async def print_test(self):
        print(f"{self.site} - {self.item} - {self.proxy.ip}")

    def __dict__(self):
        return {
            "site": self.site,
            "webhook": self.webhook,
            "title": self.title,
            "product": self.product,
            "delay": self.delay,
        }
