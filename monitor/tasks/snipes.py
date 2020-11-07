from bs4 import BeautifulSoup

from monitor.tasks.base import Task


class Snipes(Task):
    site = "snipes"

    async def check_product(self, data):
        soup = BeautifulSoup(data, "lxml")
        hook_data = []
        for wrapper in soup.findAll(attrs={"class": "b-pdp-size-wrapper"}):
            for tag in wrapper.findAll(attrs={"class": "b-size-value"}):
                item = self.stock.get(tag.attrs["data-attr-value"])
                if item is not None:
                    if not self.stock.get(item) and "b-swatch-value--orderable" in tag.attrs["class"]:
                        self.stock[item] = True
                        hook_data.append(item)
                    else:
                        self.stock[item] = False
                else:
                    item = tag.attrs["data-attr-value"]
                    in_stock: bool = "b-swatch-value--orderable" in tag.attrs["class"]
                    self.stock.update({item: in_stock})
                    if in_stock:
                        hook_data.append(item)

        if hook_data:
            await self._send_webhook(hook_data)
