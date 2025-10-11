import math
import random
from copy import deepcopy

class TicTacToe:
    def __init__(self):
        self.board = [' '] * 9
        self.current_player = 'X'

    def available_moves(self):
        return [i for i in range(9) if self.board[i] == ' ']

    def make_move(self, move):
        new_state = deepcopy(self)
        new_state.board[move] = self.current_player
        new_state.current_player = 'O' if self.current_player == 'X' else 'X'
        return new_state

    def winner(self):
        wins = [(0,1,2),(3,4,5),(6,7,8),
                (0,3,6),(1,4,7),(2,5,8),
                (0,4,8),(2,4,6)]
        for a,b,c in wins:
            if self.board[a] == self.board[b] == self.board[c] != ' ':
                return self.board[a]
        return None

    def is_terminal(self):
        return self.winner() is not None or ' ' not in self.board


class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.wins = 0

    def expand(self):
        for move in self.state.available_moves():
            if move not in self.children:
                self.children[move] = Node(self.state.make_move(move), parent=self)

    def best_child(self, c=1.4):
        return max(
            self.children.items(),
            key=lambda kv: kv[1].wins / (kv[1].visits + 1e-6) + c * math.sqrt(math.log(self.visits + 1) / (kv[1].visits + 1e-6))
        )[1]

    def simulate(self):
        state = deepcopy(self.state)
        while not state.is_terminal():
            move = random.choice(state.available_moves())
            state = state.make_move(move)
        winner = state.winner()
        if winner == self.state.current_player:
            return 1
        elif winner is None:
            return 0.5
        else:
            return 0

    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(1 - result)


def mcts(root_state, iter_max=500):
    root = Node(root_state)
    for _ in range(iter_max):
        node = root
        # 1. Selection
        while node.children:
            node = node.best_child()
        # 2. Expansion
        if not node.state.is_terminal():
            node.expand()
            node = random.choice(list(node.children.values()))
        # 3. Simulation
        result = node.simulate()
        # 4. Backpropagation
        node.backpropagate(result)
    # 选择访问次数最多的节点
    best_move = max(root.children.items(), key=lambda kv: kv[1].visits)[0]
    return best_move

# 测试 MCTS
game = TicTacToe()
move = mcts(game, iter_max=1000)
print(f"MCTS 推荐的首步是位置：{move}")
