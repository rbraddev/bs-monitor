class Task:
    def __init__(self, site, webhook: str, product: str, delay: int = 1):
        if self.site not in site:
            raise ValueError(f"{site} is invalid for this task")

        self.webhook: str = webhook
        self.product: str = product
        self.delay: int = delay

    async def setup(self):
        return NotImplemented

    async def monitor(self):
        return NotImplemented
