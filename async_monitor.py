import asyncio

import aiofiles
import yaml


class AsyncMonitor:
    def __init__(self):
        self.q: asyncio.Queue = None
        self.tasks: list = []
        self.max_workers: int = 10

    async def update_tasks(self):
        while True:
            async with aiofiles.open("test_tasks.yml") as f:
                tasks = await f.read()
            tasks = yaml.safe_load(tasks)

            print(tasks)
            for task in tasks:
                if task not in self.tasks:
                    self.tasks.append(task)
                    await self.q.put(task)
            await asyncio.sleep(5)

    async def _worker(self, name: int):
        while True:
            data = await self.q.get()
            print(data)
            self.q.task_done()
            await asyncio.sleep(1)
            if data in self.tasks:
                await self.q.put(data)

    async def _start_tasks(self):
        self.q = asyncio.Queue()
        tasks = asyncio.create_task(self.update_tasks())
        for i in range(self.max_workers):
            asyncio.create_task(self._worker(i))
        await asyncio.gather(tasks)
        await self.q.join()

        # for w in

    def run(self):
        try:
            asyncio.run(self._start_tasks())
        except KeyboardInterrupt:
            print("Monitor exited")


am = AsyncMonitor()
am.run()
