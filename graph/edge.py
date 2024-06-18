

class Edge:
    def __init__(self):
        self.next_node = None

    def run(self, data):
        pass

    def to_dict(self):
        return {
            'type': self.__class__.__name__,
            'next_node': self.next_node.to_dict() if self.next_node else None
        }

    @staticmethod
    def from_dict(edge_dict):
        edge_type = edge_dict['type']
        edge = globals()[edge_type]()
        edge.next_node = Node.from_dict(edge_dict['next_node']) if edge_dict['next_node'] else None
        return edge


class SimpleEdge(Edge):
    def run(self, data):
        if self.next_node:
            self.next_node.run(data)


class IfElseEdge(Edge):
    def __init__(self, condition):
        super().__init__()
        self.condition = condition
        self.true_node = None
        self.false_node = None

    def run(self, data):
        if self.condition.evaluate(data):
            if self.true_node:
                self.true_node.run(data)
        else:
            if self.false_node:
                self.false_node.run(data)

    def to_dict(self):
        return {
            'type': self.__class__.__name__,
            'condition': self.condition.to_dict(),
            'true_node': self.true_node.to_dict() if self.true_node else None,
            'false_node': self.false_node.to_dict() if self.false_node else None
        }

    @staticmethod
    def from_dict(edge_dict):
        condition = Condition.from_dict(edge_dict['condition'])
        edge = IfElseEdge(condition)
        edge.true_node = Node.from_dict(edge_dict['true_node']) if edge_dict['true_node'] else None
        edge.false_node = Node.from_dict(edge_dict['false_node']) if edge_dict['false_node'] else None
        return edge


class RouteEdge(Edge):
    def __init__(self, conditions):
        super().__init__()
        self.conditions = conditions  # List of (Condition, Node) pairs
        self.default_node = None

    def run(self, data):
        for condition, node in self.conditions:
            if condition.evaluate(data):
                node.run(data)
                return
        if self.default_node:
            self.default_node.run(data)

    def to_dict(self):
        return {
            'type': self.__class__.__name__,
            'conditions': [(cond.to_dict(), node.to_dict()) for cond, node in self.conditions],
            'default_node': self.default_node.to_dict() if self.default_node else None
        }

    @staticmethod
    def from_dict(edge_dict):
        conditions = [(Condition.from_dict(cond), Node.from_dict(node)) for cond, node in edge_dict['conditions']]
        edge = RouteEdge(conditions)
        edge.default_node = Node.from_dict(edge_dict['default_node']) if edge_dict['default_node'] else None
        return edge