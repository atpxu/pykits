class Node:
    def __init__(self, idx=-1, edge=None):
        self.idx = idx
        self.edge = edge

    def run(self, storage):
        if self.edge:
            self.edge.run(storage)

    def dump(self):
        return {
            'idx': self.idx,
            'cls': self.__class__.__name__,
            'edge': self.edge.idx if self.edge else None}

    def fill_from(self, dct):
        pass

    @staticmethod
    def loads(node_dict):
        node = Node()
        node.edge = Edge.from_dict(node_dict['edge']) if node_dict['edge'] else None
        return node
