from typing import Sequence

from .cond import Condition


class Edge:
    """
    Edge is a connection between two nodes.
    This parent class implements the basic methods for an edge.
    And it ends with no next node.
    """

    def get_nodes(self):
        return []

    def run(self, storage):
        pass

    async def arun(self, storage):
        pass

    def dump(self):
        return {'type': self.__class__.__name__}

    def fill(self, edge_data: dict, node_dict: dict):
        pass

    @staticmethod
    def load(edge_data: dict, node_dict: dict):
        type_ = edge_data.get('type')
        edge = globals()[type_]()
        edge.fill(edge_data, node_dict)
        return edge


class SimpleEdge(Edge):
    from .node import Node

    def __init__(self, next_node: Node = None):
        super().__init__()
        self.next_node = next_node

    def get_nodes(self):
        return [self.next_node]

    def run(self, storage):
        if self.next_node is not None:
            return self.next_node.run(storage)

    async def arun(self, storage):
        if self.next_node is not None:
            return await self.next_node.arun(storage)

    def dump(self):
        return {
            'type': self.__class__.__name__,
            'node_idx': self.next_node.idx if self.next_node else None
        }

    def fill(self, edge_data: dict, node_dict: dict):
        self.next_node = node_dict.get(edge_data.get('node_idx'))


class IfElseEdge(Edge):
    from .node import Node

    def __init__(
            self, conditions: Sequence[Condition] = (),
            is_and: bool = True,
            true_node: Node = None,
            false_node: Node = None):
        super().__init__()
        self.conditions = conditions
        self.is_and = is_and
        self.true_node = true_node
        self.false_node = false_node

    def get_nodes(self):
        return [self.true_node, self.false_node]

    def satisfy_all(self, storage):
        if self.is_and:
            for cond in self.conditions:
                if not cond.satisfy(storage):
                    return False
            return True
        else:
            for cond in self.conditions:
                if cond.satisfy(storage):
                    return True
            return False

    def run(self, storage):
        if self.satisfy_all(storage):
            if self.true_node:
                self.true_node.run(storage)
        else:
            if self.false_node:
                self.false_node.run(storage)

    async def arun(self, storage):
        if self.satisfy_all(storage):
            if self.true_node:
                await self.true_node.arun(storage)
        else:
            if self.false_node:
                await self.false_node.arun(storage)

    def dump(self):
        return {
            'type': self.__class__.__name__,
            'conditions': [cond.dump() for cond in self.conditions],
            'is_and': self.is_and,
            'true_idx': self.true_node.idx if self.true_node else None,
            'false_idx': self.false_node.idx if self.false_node else None
        }

    def fill(self, edge_data: dict, node_dict: dict):
        self.conditions = [Condition.load(x) for x in edge_data.get('conditions')]
        self.is_and = edge_data.get('is_and', True)
        self.true_node = node_dict.get(edge_data.get('true_idx'))
        self.false_node = node_dict.get(edge_data.get('false_idx'))


class RouteEdge(Edge):
    from .node import Node

    def __init__(self, routes: Sequence[tuple[Condition, Node]], default_node: Node = None):
        super().__init__()
        self.routes = routes  # List of (Condition, Node) pairs
        self.default_node = default_node

    def get_nodes(self):
        return [node for _, node in self.routes] + [self.default_node]

    def run(self, data):
        for condition, node in self.routes:
            if condition.satisfy(data):
                return node.run(data)
        if self.default_node:
            return self.default_node.run(data)

    async def arun(self, data):
        for condition, node in self.routes:
            if condition.satisfy(data):
                return await node.arun(data)
        if self.default_node:
            return await self.default_node.arun(data)

    def dump(self):
        return {
            'type': self.__class__.__name__,
            'routes': [(cond.dump(), node.idx) for cond, node in self.routes],
            'default_node': self.default_node.idx if self.default_node else None
        }

    def fill(self, edge_data: dict, node_dict: dict):
        self.routes = [
            (Condition.load(cond), node_dict[node_idx])
            for cond, node_idx in edge_data.get('routes')]
        self.default_node = node_dict.get(edge_data.get('default_node'))
