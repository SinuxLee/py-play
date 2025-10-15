from collections import namedtuple, deque
from maze_gen import maze_with_branches, print_maze

Pos = namedtuple("Pos", ["r", "c"])
Node = namedtuple("Node", ["pos", "path"])


def breadth_first_search(maze: list[list[int]]) -> list[tuple[int, int]] | None:
    max_row = len(maze)
    max_col = len(maze[0])
    target = (max_row - 1, max_col - 1)

    queue: deque[Node] = deque()  # pending for visting
    visted: set[Pos] = set()  # closed set
    directions = [
        (-1, 0),  # top
        (0, 1),  # right
        (1, 0),  # down
        (0, -1),  # left
    ]  # distance bettwen currnt node and neighbors

    start = Pos(0, 0)
    queue.append(Node(pos=start, path=[start]))  # starting node
    while len(queue) > 0:
        node = queue.popleft()  #! The key points of difference between BFS and DFS
        pos = node.pos

        # already visted so ignore it
        if pos in visted:
            continue

        # find target
        if pos == target:
            return node.path

        visted.add(pos)

        # calc neighbor and push to stack
        for x, y in [tuple(x + y for x, y in zip(pos, s)) for s in directions]:
            if y < 0 or y >= max_row or x < 0 or x >= max_col:
                continue

            neighbor = Pos(x, y)
            if neighbor in visted or maze[x][y] > 0:  # prune bad neighbors
                continue

            # not vist and inbounds
            queue.append(Node(pos=Pos(x, y), path=node.path + [neighbor]))


if __name__ == "__main__":
    """
    Handle three things:
    1. Closed set those are visted already
    2. Check current node for matching target and calculating his neighbors
    3. Filter neighbors to vist in the future
    """
    matrix = maze_with_branches(8, 8)
    print_maze(matrix)

    # 需要明确的起点和终点
    # 优化方向：双向 BFS (Bidirectional BFS)
    answer = breadth_first_search(matrix)
    print(answer)
