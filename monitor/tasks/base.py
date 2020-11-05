from monitor.proxy import Proxy


class Task:
    def __init__(self, site, webhook: str, item: str, delay: int = 1, proxy: Proxy = None):
        if self.site not in site:
            raise ValueError(f"{site} is invalid for this task")

        self.webhook: str = webhook
        self.item: str = item
        self.delay: int = delay
        self.proxy: Proxy = proxy

    async def setup(self):
        return NotImplemented

    async def monitor(self):
        return NotImplemented

    async def print_test(self):
        print(f"{self.site} - {self.item} - {self.proxy.ip}")

    def __dict__(self):
        return {
            "site": self.site,
            "webhook": self.webhook,
            "item": self.item,
            "delay": self.delay,
        }
