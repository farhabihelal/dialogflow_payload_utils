import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from abc import ABC, abstractmethod


def dfs(root):
    stack = []
    visited = []

    stack.append(root)

    while len(stack) > 0:
        node = stack.pop()
        if node.children:
            stack.extend(node.children)

        visited.append(node)

    return visited


def bfs(root):
    queue = []
    visited = []

    queue.append(root)

    while len(queue) > 0:
        node = queue.pop(0)
        if node.children:
            queue.extend(node.children)
        visited.append(node)

    return visited


def get_dfs_data():
    pass


def get_bfs_data():
    pass


class ExportAlgorithm(ABC):
    def __init__(self) -> None:
        pass

    @classmethod
    @abstractmethod
    def get_data(self, loaded_data=None):
        return loaded_data


class ExportGeneric(ExportAlgorithm):
    def __init__(self) -> None:
        super().__init__()

    def get_data(self, loaded_data=None):
        return super().get_data(loaded_data)


class ExportBFS(ExportAlgorithm):
    def __init__(self) -> None:
        super().__init__()

    def get_bfs_data(self, root_intents=None):

        data = {}
        for root in root_intents:
            children = bfs(root)
            data[root.intent_obj.display_name] = children

        return {k: data[k] for k in sorted(data.keys())}

    def get_data(self, loaded_data=None, root_intents: list = None):
        super().get_data(loaded_data)

        bfs_data = self.get_bfs_data(root_intents)

        bfs_data_flattened = []
        for intents in bfs_data.values():
            bfs_data_flattened.extend([x.display_name for x in intents])

        data = {k: loaded_data[k] for k in bfs_data_flattened}

        return data


class ExportDFS(ExportAlgorithm):
    def __init__(self) -> None:
        super().__init__()

    def get_dfs_data(self, root_intents=None):

        data = {}
        for root in root_intents:
            children = dfs(root)
            data[root.intent_obj.display_name] = children

        return {k: data[k] for k in sorted(data.keys())}

    def get_data(self, loaded_data=None, root_intents: list = None):
        super().get_data(loaded_data)

        dfs_data = self.get_dfs_data(root_intents)

        dfs_data_flattened = []
        for intents in dfs_data.values():
            dfs_data_flattened.extend([x.display_name for x in intents])

        data = {k: loaded_data[k] for k in dfs_data_flattened}

        return data
