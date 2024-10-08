from abc import ABC, abstractmethod


class Runnable(ABC):

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    @abstractmethod
    async def arun(self, *args, **kwargs):
        pass
