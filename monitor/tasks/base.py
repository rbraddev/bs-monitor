import json

import httpx


class Task:
    def __init__(self, site, webhook: str, release_link: str, delay: int = 1):
        if self.site not in site:
            raise ValueError(f"{site} is invalid for this task")

        self.webhook: str = webhook
        self.release_link: str = release_link
        self.delay: int = delay
        self.client: httpx.AsyncClient = None
        self.etag: str = None

    async def monitor(self):
        if self.client is None:
            self.client = httpx.AsyncClient()

        if self.release_link:
            await self.check_releases()

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

    def __dict__(self):
        return {
            "site": self.site,
            "webhook": self.webhook,
            "release_link": self.release_link,
            "delay": self.delay,
        }
