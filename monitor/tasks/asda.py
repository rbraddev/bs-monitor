import json

from monitor.tasks.base import Task


class Asda(Task):
    site: str = "asda"
    product_url: str = "https://direct.asda.com/george/toys-character/gaming-clothing-home-toys/playstation5-console/051003646,default,pd.html"
    user_agent: str = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 iOSNative"

    @property
    def url(self) -> str:
        return f"https://direct.asda.com/on/demandware.store/Sites-ASDA-Site/default/Product-GetPriceData?pid={self.product}&countryCode=UK&currencyCode=GBP"

    async def check_product(self, data):
        self.stock: int = json.loads(data)["productAvailability"][self.product]["availability"]["inStockQty"]
        instock: bool = json.loads(data)["productAvailability"][self.product]["availability"]["instock"]
        if instock and self.stock > 0:
            await self._send_webhook()
