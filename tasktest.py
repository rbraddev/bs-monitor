import asyncio
import yaml

import aiofiles


class Test:
    def __init__(self):
        self.q: asyncio.Queue = asyncio.Queue()
        self.workers = 10
        self.tasks = []

    async def start_tasks(self):
        await asyncio.create_task(self.update_tasks({"timeout": 5}))
        workers = [asyncio.create_task(self._worker(i)) for i in range(self.workers)]
        await asyncio.gather(*workers)
        # await self.q.put({"func":self.update_tasks, "timeout": 5})
        # await self.q.join()

    async def update_tasks(self, data: dict):
        while True:
            async with aiofiles.open("test_tasks.yml") as f:
                tasks = await f.read()
            tasks = yaml.safe_load(tasks)

            for task in tasks:
                if task not in self.tasks:
                    self.tasks.append(task)
                    await self.q.put({"func": self.run_task, "timeout": 1, "task": task})

            print(tasks)
            await asyncio.sleep(data["timeout"])

    async def _worker(self, name: int):
        while True:
            data = await self.q.get()
            await data["func"](data)

    async def run_task(self, data: dict):
        print(data["task"])
        await asyncio.sleep(data["timeout"])
        if data["task"] in self.tasks:
            await self.q.put(data)


w = Test()

asyncio.run(w.start_tasks())
