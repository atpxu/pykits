from typing import TypeVar, Generic, Protocol

from .node import Node, Edge


# 定义一个协议，类似于接口
class TaskProtocol(Protocol):
    def dump(self) -> str | None:
        return None

    @staticmethod
    def load(task_dict: dict):
        return TaskProtocol()

    def run(self):
        pass

    async def arun(self):
        pass


# 定义一个泛型变量
GeneralTask = TypeVar('GeneralTask', bound=TaskProtocol)


class TaskNode(Node, Generic[GeneralTask]):

    def __init__(self, idx=-1, edge: Edge = None, task: GeneralTask = None):
        super().__init__(idx, edge)
        self.task = task

    def run(self, storage):
        self.task.run()
        return super().run(storage)

    async def arun(self, storage):
        await self.task.arun()
        return await super().run(storage)

    def dump(self):
        return {
            'idx': self.idx,
            'type': self.__class__.__name__,
            'task': self.task.dump(),
            'edge': self.edge.dump() if self.edge else None
        }

    def fill(self, node_dict):
        self.task = GeneralTask.load(node_dict['task'])
