from collections import namedtuple, deque
from maze_gen import maze_with_branches, print_maze

Pos = namedtuple("Pos", ["r", "c"])
Node = namedtuple("Node", ["pos", "path"])


def depth_first_search_stack(maze: list[list[int]]) -> list[tuple[int, int]] | None:
    max_row = len(maze)
    max_col = len(maze[0])
    target = (max_row - 1, max_col - 1)

    stack: deque[Node] = deque()  # pending for visting
    visted: set[Pos] = set()  # closed set
    directions = [
        (-1, 0),  # top
        (0, 1),  # right
        (1, 0),  # down
        (0, -1),  # left
    ]  # distance bettwen currnt node and neighbors

    start = Pos(0, 0)
    stack.append(Node(pos=start, path=[start]))  # starting node
    while len(stack) > 0:
        node = stack.pop()
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
            if neighbor in visted or maze[x][y] > 0:
                continue

            # not vist and inbounds
            stack.append(Node(pos=Pos(x, y), path=node.path + [neighbor]))


def recurse_search(maze: list[list[int]], visted: set[Pos], target: Pos, curr: Node):
    pos = curr.pos
    if pos in visted:
        return

    if pos == target:
        return curr.path

    visted.add(pos)

    steps = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    max_row = len(maze)
    max_col = len(maze[0])

    # calc neighbor then vist it
    for x, y in [tuple(x + y for x, y in zip(pos, s)) for s in steps]:
        if y < 0 or y >= max_row or x < 0 or x >= max_col:
            continue

        neighbor = Pos(x, y)
        if neighbor in visted or maze[x][y] > 0:
            continue

        result = recurse_search(
            maze, visted, target, Node(pos=Pos(x, y), path=curr.path + [neighbor])
        )

        if result:
            return result


def depth_first_search_recursion(maze: list[list[int]]) -> list[tuple[int, int]] | None:
    max_row = len(maze)
    max_col = len(maze[0])
    target = (max_row - 1, max_col - 1)
    visted: set[Pos] = set()  # 已访问过的位置

    return recurse_search(maze, visted, target, Node(pos=(0, 0), path=[(0, 0)]))


if __name__ == "__main__":
    """
    Handle three things:
    1. Closed set those are visted already
    2. Check current node for matching target and calculating his neighbors
    3. Filter neighbors to vist in the future
    """
    matrix = maze_with_branches(8, 8)
    print_maze(matrix)

    # 递归和非递归计算出的结果可能不一样
    # 深度优先，可能会走入一个很深的死胡同，然后在回溯。
    # 扩展：左手法则走迷宫，适合 perfect maze。还有 Tremaux 算法
    answer = depth_first_search_stack(matrix)
    print(answer)

    answer = depth_first_search_recursion(matrix)
    print(answer)
