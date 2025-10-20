import tkinter as tk
from tkinter import messagebox
import math


# ---------- 游戏逻辑 ----------
def check_winner(board):
    win_lines = [
        # 横着连成一条线
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        # 竖着连成线
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        # 对角线连成线
        [0, 4, 8],
        [2, 4, 6],
    ]

    for a, b, c in win_lines:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]

    # 和棋
    if all(board):
        return "Draw"

    return None


def minimax(board, depth, is_maximizing, alpha, beta):
    """
    对于 MAX 节点来说，α 是当前已知的“至少能得到这么多分”
    对于 MIN 节点来说，β 是当前已知的“最多会被扣到这么多分”
    当 α ≥ β 时，说明对方不会让你达到这个分数
    这是个零和问题，我方想至少得到60分，但对方最多只会丢失50分。60 > 50,所以目标不会达成。
    """
    winner = check_winner(board)
    if winner == "X":
        return -1
    elif winner == "O":
        return 1
    elif winner == "Draw":
        return 0

    if is_maximizing:
        max_eval = -math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "O"
                eval = minimax(board, depth + 1, False, alpha, beta)
                board[i] = ""
                # 选一个最优的，则为我最少得分着法
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if alpha >= beta:
                    break
        return max_eval
    else:
        min_eval = math.inf  # 找最小值
        for i in range(9):
            if board[i] == "":
                board[i] = "X"

                # 对手最多让我得分
                eval = minimax(board, depth + 1, True, alpha, beta)
                board[i] = ""

                # 取最小的，即对手给我的最多得分
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)

                # 我已找到最少等分路径
                if alpha >= beta:
                    break
        return min_eval


def best_move(board):
    best_val = -math.inf
    move = None
    for i in range(9):
        if board[i] == "":
            board[i] = "O"
            move_val = minimax(board, 0, False, -math.inf, math.inf)
            board[i] = ""
            if move_val > best_val:
                best_val = move_val
                move = i
    return move


# ---------- Tkinter 界面 ----------
class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("井字棋 AI - Minimax + Alpha-Beta")
        self.board = [""] * 9
        self.buttons = []
        self.create_board()

    def create_board(self):
        for i in range(9):
            button = tk.Button(
                self.root,
                text="",
                font=("Helvetica", 32, "bold"),
                width=5,
                height=2,
                command=lambda i=i: self.player_move(i),
            )
            button.grid(row=i // 3, column=i % 3)
            self.buttons.append(button)

    def player_move(self, i):
        if self.board[i] == "" and not check_winner(self.board):
            self.board[i] = "X"
            self.buttons[i].config(text="X", disabledforeground="blue")
            self.buttons[i]["state"] = "disabled"
            winner = check_winner(self.board)
            if winner:
                self.end_game(winner)
                return
            self.root.after(300, self.ai_move)

    def ai_move(self):
        move = best_move(self.board)
        if move is not None:
            self.board[move] = "O"
            self.buttons[move].config(text="O", disabledforeground="red")
            self.buttons[move]["state"] = "disabled"
        winner = check_winner(self.board)
        if winner:
            self.end_game(winner)

    def end_game(self, winner):
        if winner == "Draw":
            messagebox.showinfo("游戏结束", "平局！")
        else:
            messagebox.showinfo("游戏结束", f"胜者是: {winner}")
        self.reset_board()

    def reset_board(self):
        self.board = [""] * 9
        for b in self.buttons:
            b.config(text="", state="normal")


# ---------- 启动游戏 ----------
if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToeGUI(root)
    root.mainloop()
