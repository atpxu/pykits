import asyncio
from contextlib import asynccontextmanager


class AsyncRotatingClientPool:
    """
    Wraps a client class and provides a pool of clients to use.
    Each client uses a different endpoint.
    """

    def __init__(self, client_cls: type, endpoints: list[str] | str, conn_per_url: int = 1):
        """
        :param client_cls: the client class to wrap
        :param endpoints: list of URLs to connect to for the clients
        :param conn_per_url: count of connections per each endpoint
        """
        if isinstance(endpoints, str):
            endpoints = [endpoints]
        self.clients = [
            {'client': client_cls(endpoint), 'in_use': False}
            for endpoint in endpoints * conn_per_url
        ]
        self.condition = asyncio.Condition()

    @asynccontextmanager
    async def get_client(self):
        client = await self._acquire_client()
        try:
            yield client
        finally:
            if client:
                await self._release_client(client)

    async def _acquire_client(self):
        async with self.condition:
            while True:
                for client_info in self.clients:
                    if not client_info['in_use']:
                        client_info['in_use'] = True
                        return client_info['client']
                # 如果所有客户端都在使用中，等待条件通知
                await self.condition.wait()

    async def _release_client(self, client):
        async with self.condition:
            for client_info in self.clients:
                if client_info['client'] is client:
                    client_info['in_use'] = False
                    break
            # 仍然持有锁，通知等待的线程有客户端可用了
            self.condition.notify_all()
        # 锁在这里被释放，当离开with self.condition块时
