import json

from monitor.tasks.base import Task


class JohnLewis(Task):
    site = "johnlewis"
    product_url: str = "https://www.johnlewis.com/sony-playstation-5-console-with-dualsense-controller/p5115192"
    user_agent = "JohnLewis/6.41.1 iPhone13,4 iOS/15.0.1 CFNetwork/1312 Darwin/21.0.0"

    @property
    def url(self) -> str:
        return f"https://api.johnlewis.com/mobile-apps/api/v1/products/{self.product}"

    async def check_product(self, data):
        self.stock: int = json.loads(data)["skus"][0]["availability"]["stockLevel"]
        if self.stock > 0:
            await self._send_webhook()
