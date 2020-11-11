import httpx

from monitor.tasks.base import Task


class Graffitishop(Task):
    site = "graffitishop"

    async def _check_releases(self):
        try:
            headers = {"Accept": "application/json"}
            if self.etag:
                headers.update({"If-None-Match": self.etag})

            results = await self.client.get(url=self.release_link, headers=headers)

            if results.status_code == httpx.codes.OK:
                if results.headers.get("etag"):
                    self.etag = results.headers.get("etag")

                await self._get_updates(results.json())

            if results.status_code == httpx.codes.INTERNAL_SERVER_ERROR:
                print(f"{self.site.capitalize()} Monitor: Internal server error - {self.release_link}")

            if results.status_code == 304:
                print(f"{self.site}: {self.release_link} - NO UPDATES")

        except httpx.ConnectError:
            print(f"{self.site.capitalize()} Monitor: Error connecting to {self.release_link}")

    async def _get_updates(self, data: list):
        new_items = self._parse_items(data)
        original_items, self.items = self.items, new_items

        for key, data in self.items.items():
            original_item = original_items.get(key)
            if not original_item and data["url"]:
                await self._send_webhook(item=key, url=data["url"], img=data["img"])

            if original_item and original_item["url"] != data["url"] and not data["url"]:
                await self._send_webhook(item=key, url=data["url"], img=data["img"])

    def _parse_items(self, data: list) -> dict:
        parsed_items = {
            item["name"]: {"date": item["date"], "url": item["url"], "img": item["img"]}
            for item in data
            if item["name"]
        }

        return parsed_items
