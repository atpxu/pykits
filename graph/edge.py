from typing import Sequence

from .cond import Condition


class Edge:
    """
    Edge is a connection between two nodes in the graph.
    This parent class implements the basic methods for an edge.
    And it ends with no node to connect.
    """
    from .node import Node  # Avoid circular import

    def get_nodes(self) -> list[Node]:
        """
        Get a list of nodes connected by this edge.
        :return:
        """
        return []

    def run(self, storage):
        """Run the task inside the node and then goto the edge"""
        pass

    async def arun(self, storage):
        """Async version of run()"""
        pass

    def dump(self) -> dict:
        """Dump to a dict for serialization"""
        return {'type': self.__class__.__name__}

    def fill(self, edge_data: dict, node_dict: dict) -> None:
        """Fill edge data and corresponding node data into the edge object."""
        pass

    @staticmethod
    def load(edge_data: dict, node_dict: dict):
        """Load an edge from a dict as deserialization."""
        type_ = edge_data.get('type')
        edge = globals()[type_]()
        edge.fill(edge_data, node_dict)
        return edge


class SimpleEdge(Edge):
    """
    SimpleEdge is a direct connection between two nodes.
    """
    from .node import Node

    def __init__(self, next_node: Node = None):
        """

        :param next_node: the node connected by this edge
        """
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
    """
    IfElseEdge is a connection with multiple conditions.
    """
    from .node import Node

    def __init__(
            self, conditions: Sequence[Condition] = (),
            is_and: bool = True,
            true_node: Node = None,
            false_node: Node = None):
        """
        :param conditions: a list of conditions
        :param is_and: if True, all conditions should be satisfied, otherwise, any one of them is enough
        :param true_node: the node to run when conditions are satisfied
        :param false_node: the node to run when conditions are not satisfied
        """
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
    """
    RouteEdge is a connection with multiple routes. Each route has a condition to satisfy.
    If none of the conditions is satisfied, the default node will be run.
    """
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
