import numpy as np
import matplotlib.pyplot as plt
import random
from copy import deepcopy

BOARD_SIZE = 10

# 一些基础形状（可扩展）
SHAPES: list[np.ndarray] = [
    np.array([[1]]),
    np.array([[1, 1]]),
    np.array([[1], [1]]),
    np.array([[1, 1, 1]]),
    np.array([[1], [1], [1]]),
    np.array([[1, 1], [1, 1]]),
    np.array([[1, 1, 1], [1, 0, 0]]),
    np.array([[1, 1, 1], [0, 0, 1]]),
    np.array([[1, 0], [1, 1]]), # L
    np.array([[0, 1], [1, 1]]), # J
    np.array([[1, 1], [0, 1]]),
    np.array([[1, 1, 1, 1]]),
    np.array([[1], [1], [1], [1]]),
    np.array([[1, 1, 1], [0, 1, 0]]), # T
    np.array([[1, 1, 1], [1, 1, 1]])
]


def random_shapes(n=3):
    return [random.choice(SHAPES) for _ in range(n)]


class Game1010:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.score = 0

    def can_place(self, shape, r, c):
        h, w = shape.shape
        if r + h > BOARD_SIZE or c + w > BOARD_SIZE:
            return False
        region = self.board[r : r + h, c : c + w]
        return np.all(region + shape <= 1)

    def place(self, shape, r: int, c: int):
        h, w = shape.shape
        self.board[r : r + h, c : c + w] += shape
        return self.clear_lines()

    def clear_lines(self):
        """消除的行/列数"""
        full_rows = np.where(np.all(self.board == 1, axis=1))[0]
        full_cols = np.where(np.all(self.board == 1, axis=0))[0]
        cleared = len(full_rows) + len(full_cols)
        for r in full_rows:
            self.board[r, :] = 0
        for c in full_cols:
            self.board[:, c] = 0
        self.score += cleared * 10
        return cleared

    def available_moves(self, shape):
        moves: list[tuple[int, int]] = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.can_place(shape, r, c):
                    moves.append((r, c))
        return moves

    def count_holes(self):
        """孤立空洞数"""
        holes = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r, c] == 0:
                    # 如果四周都是1则算孤立洞
                    neigh = self.board[max(0, r - 1) : r + 2, max(0, c - 1) : c + 2]
                    if np.all(neigh == 1) == False:
                        holes += 1
        return holes

    def mobility(self):
        """下一步可放置形状数"""
        count = 0
        for s in SHAPES:
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if self.can_place(s, r, c):
                        count += 1
                        break
        return count

    def heuristic_score(self, cleared):
        empty = np.sum(self.board == 0)  # 剩余空格数
        holes = self.count_holes()
        mobility = self.mobility()
        score = (cleared * 5) + (mobility * 2) - (holes * 3) - (empty * 0.1)
        return score


def evaluate_move(state: Game1010, shape, move: tuple[int, int], samples=3):
    """Monte Carlo Rollouts（蒙特卡洛随机模拟）
        评估一个好的操作

    Args:
        state (Game1010): _description_
        shape (_type_): _description_
        move (tuple[int, int]): _description_
        samples (int, optional): _description_. Defaults to 3.
        depth (int, optional): _description_. Defaults to 3.

    Returns:
        _type_: _description_
    """
    total = 0
    for _ in range(samples):
        sim = deepcopy(state)
        cleared = sim.place(shape, *move)
        score = sim.heuristic_score(cleared)
        total += score
    return total / samples


def best_move(state: Game1010, shapes):
    best_score = -1e9
    best = None
    for shape in shapes:
        moves = state.available_moves(shape)
        for move in moves:
            score = evaluate_move(state, shape, move, 3)
            if score > best_score:
                best_score = score
                best = (shape, move)
    return best, best_score


def show_board(board, step, score):
    plt.imshow(board, cmap="Greens", vmin=0, vmax=1)
    plt.title(f"Step {step}  |  Score: {score}")
    plt.xticks(range(BOARD_SIZE))
    plt.yticks(range(BOARD_SIZE))
    plt.grid(color="gray", linestyle="--", linewidth=0.5)
    plt.pause(0.4)  # 控制动画速度


# ---------- 主逻辑 ----------
game = Game1010()
rounds = 0
show_ui = False

if show_ui:
    plt.figure(figsize=(5, 5))
    plt.ion()  # 开启交互模式

while True:
    shapes = random_shapes(3)
    best, score = best_move(game, shapes)
    if not best:
        print(f"游戏结束！总分：{game.score}")
        break
    shape, move = best
    game.place(shape, *move)
    rounds += 1

    print(f"第 {rounds} 回合：放置形状 {shape.shape} 于 {move}，得分 {game.score}")
    if show_ui:
        show_board(game.board, rounds, game.score)
if show_ui:
    plt.ioff()
    plt.show()
