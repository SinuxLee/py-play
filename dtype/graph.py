from collections import defaultdict, deque


class AdjacencyList:
    """
    邻接表
    哈希表+链表
    """

    def __init__(self):
        self.data: defaultdict[str, list[str]] = defaultdict(list[str])

    def parse(self, data: str = "0:1;1:0,2;2:1"):
        for item in data.split(";"):
            k, v = item.split(":")
            for e in v.split(","):
                self.data[k].append(e)

    def display(self):
        for k, v in self.data.items():
            print(k, v)


class AdjacencyMatrix:
    """
    邻接矩阵
    哈希表记录节点位置
    矩阵表示节点间联通性
    """

    def __init__(self, count):
        self.data: list[list[int]] = [[0] * count for _ in range(count)]
        self.nodes: dict[str, int] = {}

    def parse(self, data: str = "1>0:2;2>1:4;9>7:100;0>1:10"):
        items = data.split(";")
        keys = [item.split(":")[0].split(">") for item in items]
        flat_keys = [x for sub in keys for x in sub]
        ndim = len(list(dict.fromkeys(flat_keys)))

        self.data: list[list[int]] = [[0] * ndim for _ in range(ndim)]
        for item in items:
            r, w = item.split(":")
            fr, to = r.split(">")
            if fr not in self.nodes:
                self.nodes[fr] = len(self.nodes)

            if to not in self.nodes:
                self.nodes[to] = len(self.nodes)

            fr_idx = self.nodes.get(fr, len(self.nodes))
            to_idx = self.nodes.get(to, len(self.nodes))
            self.data[fr_idx][to_idx] = w

    def display(self):
        print(self.nodes)
        print(self.data)


def topological_sort(num_nodes, edges):
    graph = defaultdict(list)
    in_degree = [0] * num_nodes

    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    queue = deque([i for i in range(num_nodes) if in_degree[i] == 0])
    topo_order = []

    while queue:
        node = queue.popleft()
        topo_order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(topo_order) == num_nodes:
        return topo_order
    else:
        return []  # 有环，不存在拓扑排序


def dag_longest_path(num_nodes, edges):
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))

    # 拓扑排序
    topo_order = topological_sort(num_nodes, [(u, v) for u, v, _ in edges])

    dist = [-float("inf")] * num_nodes
    dist[topo_order[0]] = 0  # 起点

    for u in topo_order:
        for v, w in graph[u]:
            if dist[u] + w > dist[v]:
                dist[v] = dist[u] + w
    return dist


if __name__ == "__main__":
    g = AdjacencyList()
    g.parse()
    g.display()

    print("=" * 8)
    g = AdjacencyMatrix(3)
    g.parse()
    g.display()

    print("=" * 8)
    # DAG 拓扑排序
    num_nodes = 6
    edges = [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)]
    print(topological_sort(num_nodes, edges))

    # 动态规划中利用拓扑排序
    num_nodes = 6
    edges = [(0, 1, 5), (0, 2, 3), (1, 3, 6), (2, 3, 7), (3, 4, 4), (3, 5, 2)]
    print(dag_longest_path(num_nodes, edges))
