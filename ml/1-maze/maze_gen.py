import random


def simple_maze(n: int, m: int) -> list[list[int]]:
    maze = [[1] * m for _ in range(n)]
    x, y = 0, 0
    maze[x][y] = 0  # 起点
    while x < n - 1 or y < m - 1:
        maze[x][y] = 0
        if random.choice([True, False]) and x < n - 1:
            x += 1
            continue

        if y < m - 1:
            y += 1

    maze[n - 1][m - 1] = 0  # 终点
    return maze


def maze_with_branches(n: int, m: int, extra: int = 10) -> list[list[int]]:
    maze = [[1] * m for _ in range(n)]
    # 先生成一条保证通路
    x, y = 0, 0
    maze[x][y] = 0  # 起点
    while x < n - 1 or y < m - 1:
        maze[x][y] = 0
        if random.choice([True, False]) and x < n - 1:
            x += 1
            continue

        if y < m - 1:
            y += 1

    maze[n - 1][m - 1] = 0  # 终点

    # 打通额外的格子，增加分支
    for _ in range(extra):
        rx, ry = random.randint(0, n - 1), random.randint(0, m - 1)
        maze[rx][ry] = 0

    return maze


def print_maze(maze: list[list[int]]):
    for row in maze:
        print("".join("x" if c == 0 else "." for c in row))


if __name__ == "__main__":
    maze = simple_maze(5, 5)
    print_maze(maze)

    maze = maze_with_branches(10, 10)
    print_maze(maze)
