from .edge import Edge
from configurable.runnable import Runnable

class Node(Runnable):
    def __init__(self, idx=-1, edge: Edge = None):
        self.idx = idx
        self.edge = edge

    def run(self, storage):
        if self.edge:
            return self.edge.run(storage)

    async def arun(self, storage):
        if self.edge:
            return await self.edge.arun(storage)

    def dump(self):
        return {
            'idx': self.idx,
            'type': self.__class__.__name__,
            'edge': self.edge.dump() if self.edge else None}

    def fill(self, node_dict):
        pass

    @staticmethod
    def load(node_dict):
        node: Node = globals()[node_dict['type']]()
        node.idx = node_dict.get('idx', -1)
        node.edge = None
        node.fill(node_dict)
        return node

    @staticmethod
    def load_list(dicts: list[dict]):
        nodes = {}
        for dct in dicts:
            node = Node.load(dct)
            nodes[node.idx] = node

        for dct in dicts:
            idx = dct.get('idx', -1)
            node = nodes.get(idx)
            node.edge = Edge.load(dct['edge'], nodes)
        return list(nodes.values())

    def dump_list(self) -> list:
        nodes = {}

        def __dump_list(node, ndict):
            ndict[node.idx] = node.dump()
            if node.edge:
                sub_nodes = node.edge.get_nodes()
                for sub in sub_nodes:
                    if sub.idx not in ndict:
                        __dump_list(sub, ndict)

        __dump_list(self, nodes)
        return sorted(nodes.values(), key=lambda x: x['idx'])
