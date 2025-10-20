import random, math, time
import matplotlib.pyplot as plt
import pandas as pd


# Game classes (same as before, but redefined here for a clean run)
class TicTacToe:
    def __init__(self):
        self.board = [0] * 9
        self.current_player = 1

    def clone(self):
        t = TicTacToe()
        t.board = self.board[:]
        t.current_player = self.current_player
        return t

    def legal_moves(self):
        return [i for i, v in enumerate(self.board) if v == 0]

    def play(self, move):
        if self.board[move] != 0:
            raise ValueError("illegal")
        self.board[move] = self.current_player
        self.current_player *= -1

    def is_terminal(self):
        return self.get_winner() != 0 or all(v != 0 for v in self.board)

    def get_winner(self):
        B = self.board
        lines = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]
        for a, b, c in lines:
            s = B[a] + B[b] + B[c]
            if s == 3:
                return 1
            if s == -3:
                return -1
        return 0

    def result(self):
        w = self.get_winner()
        if w == 1:
            return 1.0
        if w == -1:
            return -1.0
        return 0.0


class Connect4:
    ROWS = 6
    COLS = 7

    def __init__(self):
        self.board = [[0] * Connect4.COLS for _ in range(Connect4.ROWS)]
        self.heights = [0] * Connect4.COLS
        self.current_player = 1

    def clone(self):
        c = Connect4()
        c.board = [row[:] for row in self.board]
        c.heights = self.heights[:]
        c.current_player = self.current_player
        return c

    def legal_moves(self):
        return [c for c in range(Connect4.COLS) if self.heights[c] < Connect4.ROWS]

    def play(self, col):
        if self.heights[col] >= Connect4.ROWS:
            raise ValueError("illegal")
        r = Connect4.ROWS - 1 - self.heights[col]
        self.board[r][col] = self.current_player
        self.heights[col] += 1
        self.current_player *= -1

    def is_terminal(self):
        return self.get_winner() != 0 or all(h == Connect4.ROWS for h in self.heights)

    def get_winner(self):
        B = self.board
        R = Connect4.ROWS
        C = Connect4.COLS
        for r in range(R):
            for c in range(C):
                p = B[r][c]
                if p == 0:
                    continue
                if c + 3 < C and all(B[r][c + i] == p for i in range(4)):
                    return p
                if r + 3 < R and all(B[r + i][c] == p for i in range(4)):
                    return p
                if (
                    r + 3 < R
                    and c + 3 < C
                    and all(B[r + i][c + i] == p for i in range(4))
                ):
                    return p
                if (
                    r + 3 < R
                    and c - 3 >= 0
                    and all(B[r + i][c - i] == p for i in range(4))
                ):
                    return p
        return 0

    def result(self):
        w = self.get_winner()
        if w == 1:
            return 1.0
        if w == -1:
            return -1.0
        return 0.0


# MCTS signed implementation (efficient)
def mcts_search_signed(root_state, iter_max=200, c_param=1.4):
    class Node:
        __slots__ = (
            "state",
            "parent",
            "move",
            "children",
            "_untried",
            "wins",
            "visits",
        )

        def __init__(self, state, parent=None, move=None):
            self.state = state
            self.parent = parent
            self.move = move
            self.children = {}
            self._untried = None
            self.wins = 0.0
            self.visits = 0

        def untried(self):
            if self._untried is None:
                self._untried = self.state.legal_moves()
            return self._untried

        def expand(self):
            um = self.untried()
            m = um.pop(random.randrange(len(um)))
            s = self.state.clone()
            s.play(m)
            ch = Node(s, parent=self, move=m)
            self.children[m] = ch
            return ch

        def best_child(self):
            best = None
            best_score = -1e9
            for ch in self.children.values():
                if ch.visits == 0:
                    score = float("inf")
                else:
                    score = (ch.wins / ch.visits) + c_param * math.sqrt(
                        math.log(self.visits) / ch.visits
                    )
                if score > best_score:
                    best_score = score
                    best = ch
            return best

    root = Node(root_state)
    for _ in range(iter_max):
        node = root
        # selection
        while not node.state.is_terminal() and node.untried() == []:
            node = node.best_child()
        # expansion
        if not node.state.is_terminal() and node.untried():
            node = node.expand()
        # simulation
        sim = node.state.clone()
        while not sim.is_terminal():
            mv = random.choice(sim.legal_moves())
            sim.play(mv)
        reward = sim.result()  # from perspective of player 1
        # backpropagate with sign flip to account for alternating players
        cur = node
        while cur is not None:
            cur.visits += 1
            # If the player to move at this node is -1, then the player who just moved was +1, so add reward;
            # if player to move is +1, player who just moved was -1, so add -reward.
            cur.wins += reward if cur.state.current_player == -1 else -reward
            cur = cur.parent
    if not root.children:
        return random.choice(root_state.legal_moves())
    best_move = max(root.children.items(), key=lambda item: item[1].visits)[0]
    return best_move


def play_game_vs_random(game_cls, mcts_iters, first_player_mcts=True):
    state = game_cls()
    while not state.is_terminal():
        if (state.current_player == 1 and first_player_mcts) or (
            state.current_player == -1 and not first_player_mcts
        ):
            move = mcts_search_signed(state.clone(), iter_max=mcts_iters)
        else:
            move = random.choice(state.legal_moves())
        state.play(move)
    return state.get_winner()


def run_experiment(game_name, game_cls, sim_counts, n_games):
    results = []
    for sims in sim_counts:
        wins = 0
        draws = 0
        losses = 0
        start = time.time()
        for _ in range(n_games):
            w = play_game_vs_random(game_cls, sims, first_player_mcts=True)
            if w == 1:
                wins += 1
            elif w == -1:
                losses += 1
            else:
                draws += 1
        t = time.time() - start
        results.append(
            {
                "simulations": sims,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "winrate": wins / n_games,
                "drawrate": draws / n_games,
                "lossrate": losses / n_games,
                "time_sec": t,
            }
        )
        print(
            f"{game_name} sims={sims}: win={wins}, draw={draws}, loss={losses}, time={t:.1f}s"
        )
    return pd.DataFrame(results)


# Reduced configs
ttt_sims = [10, 50, 100, 200]
c4_sims = [10, 50, 100, 200]

df_ttt = run_experiment("TicTacToe", TicTacToe, ttt_sims, n_games=80)
df_c4 = run_experiment("Connect4", Connect4, c4_sims, n_games=20)

# Plotting
plt.figure(figsize=(7, 4))
plt.plot(df_ttt["simulations"], df_ttt["winrate"], marker="o")
plt.xlabel("MCTS simulations per move")
plt.ylabel("Win rate (MCTS as first player)")
plt.title("Tic-Tac-Toe: Win rate vs simulations")
plt.grid(True)
plt.xticks(ttt_sims)
plt.ylim(-0.05, 1.05)
plt.show()

plt.figure(figsize=(7, 4))
plt.plot(df_c4["simulations"], df_c4["winrate"], marker="o")
plt.xlabel("MCTS simulations per move")
plt.ylabel("Win rate (MCTS as first player)")
plt.title("Connect4: Win rate vs simulations")
plt.grid(True)
plt.xticks(c4_sims)
plt.ylim(-0.05, 1.05)
plt.show()
