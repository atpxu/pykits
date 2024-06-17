import threading
from contextlib import contextmanager


class RotatingClientPool:
    """
    Wraps a client class and provides a pool of clients to use.
    each client uses different endpoint.
    """

    def __init__(self, client_cls: type, endpoints: list[str] | str, conn_per_url: int = 1):
        """

        :param client_cls: the client class to wrap
        :param endpoints: list of URLs to connect to for the clients
        :param conn_per_url: count of connection per each endpoint
        """
        if isinstance(endpoints, str):
            endpoints = [endpoints]
        self.clients = [
            {'client': client_cls(endpoint), 'in_use': False}
            for endpoint in endpoints * conn_per_url]
        self.condition = threading.Condition()

    @contextmanager
    def get_client(self):
        client = self._acquire_client()
        try:
            yield client
        finally:
            if client:
                self._release_client(client)

    def _acquire_client(self):
        with self.condition:
            while True:
                for client_info in self.clients:
                    if not client_info['in_use']:
                        client_info['in_use'] = True
                        return client_info['client']
                # 如果所有客户端都在使用中，等待条件通知
                self.condition.wait()

    def _release_client(self, client):
        with self.condition:
            for client_info in self.clients:
                if client_info['client'] is client:
                    client_info['in_use'] = False
                    break
            # 仍然持有锁，通知等待的线程有客户端可用了
            self.condition.notify()
        # 锁在这里被释放，当离开with self.condition块时
