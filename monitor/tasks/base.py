import json

import httpx


class Task:
    def __init__(self, site: str, webhook: str, release_link: str, delay: int = 1):
        if self.site != site:
            raise ValueError(f"{site} is invalid for this task")

        self.webhook: str = webhook
        self.release_link: str = release_link
        self.delay: int = delay
        self.client: httpx.AsyncClient = None
        self.items: dict = {}
        self.etag: str = None

    async def monitor(self):
        if self.client is None:
            self.client = httpx.AsyncClient()
        if self.release_link:
            await self._check_releases()

    async def _send_webhook(self, item: str, url: str, img: str):
        headers = {"content-type": "application/json"}
        # nl = "\n"
        payload = {
            "content": "In Stock",
            "username": "bs-monitor",
            "embeds": [{"title": self.site.capitalize(), "description": f"[{item}]({url})", "image": {"url": img}}],
        }
        async with httpx.AsyncClient() as client:
            await client.post(url=self.webhook, data=json.dumps(payload), headers=headers)

    async def _check_releases(self):
        return NotImplemented

    async def _get_updates(self, data: list):
        return NotImplemented

    def _parse_items(self, data: list) -> dict:
        pass

    def __dict__(self):
        return {
            "site": self.site,
            "webhook": self.webhook,
            "release_link": self.release_link,
            "delay": self.delay,
        }
