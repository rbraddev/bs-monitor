from monitor.tasks.base import Task


class Graffitishop(Task):
    site = "graffitishop"

    async def check_releases(self):
        try:
            headers = {"Accept": "application/json"}
            if self.etag:
                headers.update({"If-None-Match": self.etag})
            results = self.client.get(url=self.release_link, headers=headers)

            if results.status_code != 304:
                pass
        except:
            pass
