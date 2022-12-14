class Node:
    def __init__(self, value) -> None:
        self.value = value
        self.parent = None
        self.children = []

    def __repr__(self) -> str:
        return str(self.value)


def generate_tree(nodes):
    for x in nodes:
        if x.parent:
            x.parent.children.append(x)


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


if __name__ == "__main__":
    node_A = Node("A")
    node_B = Node("B")
    node_C = Node("C")
    node_D = Node("D")
    node_E = Node("E")
    node_F = Node("F")
    node_G = Node("G")

    nodes = [
        node_A,
        node_B,
        node_C,
        node_D,
        node_E,
        node_F,
        node_G,
    ]

    root = node_A
    node_B.parent = node_A
    node_C.parent = node_A
    node_D.parent = node_B
    node_E.parent = node_B
    node_F.parent = node_C
    node_G.parent = node_C

    generate_tree(nodes)
    print(bfs(root))
