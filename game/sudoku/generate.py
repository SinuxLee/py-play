# sudoku/generate.py

# 中等 30–36，困难 25–30，极难有时低至 17
# 36–45+ 容易（通常只需基础技巧）
# 30–35	 中等（需要多步逻辑推理）
# 25–29	 困难（可能需要较复杂的模式推理）
# 22–24	 很难（通常要用高级技巧或假设法）
# 17–21	 极难（多半需要搜索/回溯，人类几乎很难逻辑解完）

# 高级技巧（X-Wing、Swordfish、甚至猜测/回溯）

import random
from typing import List, Tuple, Optional

Grid = List[List[int]]

def print_grid(g: Grid) -> None:
    for r in range(9):
        row = ""
        for c in range(9):
            v = g[r][c]
            row += "." if v == 0 else str(v)
            row += " "
            if c in (2,5): row += "| "
        print(row)
        if r in (2,5):
            print("-"*21)
    print()

def grid_to_string(g: Grid) -> str:
    return ";".join("".join('.' if v==0 else str(v) for v in row) for row in g)

# 检查在 (r,c) 放 val 是否合法
def is_valid(g: Grid, r: int, c: int, val: int) -> bool:
    if any(g[r][j] == val for j in range(9)): return False
    if any(g[i][c] == val for i in range(9)): return False
    br, bc = (r//3)*3, (c//3)*3
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if g[i][j] == val:
                return False
    return True

# 生成完整解盘（回溯），返回 True 并修改 g
def generate_full_grid(g: Grid) -> bool:
    # 找未填位置
    for i in range(9):
        for j in range(9):
            if g[i][j] == 0:
                nums = list(range(1,10))
                random.shuffle(nums)
                for val in nums:
                    if is_valid(g, i, j, val):
                        g[i][j] = val
                        if generate_full_grid(g):
                            return True
                        g[i][j] = 0
                return False
    return True  # 全填好了

# 求解器：计数解的个数（上限 limit），用于检测唯一解
def count_solutions(grid: Grid, limit: int=2) -> int:
    g = [row[:] for row in grid]

    def dfs_count() -> int:
        # 找最少候选数的空格（启发式），加速
        best_r, best_c = -1, -1
        min_cand = 10
        for i in range(9):
            for j in range(9):
                if g[i][j] == 0:
                    cands = [v for v in range(1,10) if is_valid(g, i, j, v)]
                    if len(cands) == 0:
                        return 0  # 无解
                    if len(cands) < min_cand:
                        min_cand = len(cands)
                        best_r, best_c = i, j
        if best_r == -1:
            return 1  # 填满，找到 1 个解

        total = 0
        for v in range(1,10):
            if is_valid(g, best_r, best_c, v):
                g[best_r][best_c] = v
                cnt = dfs_count()
                total += cnt
                g[best_r][best_c] = 0
                if total >= limit:
                    return total
        return total

    return dfs_count()

# 挖空以得到目标 clues（保留格子数），确保唯一解
def make_puzzle_from_full(full: Grid, clues: int=30, symmetric: bool=False, random_seed: Optional[int]=None) -> Grid:
    if random_seed is not None:
        random.seed(random_seed)
    puzzle = [row[:] for row in full]
    # 所有位置列表，随机顺序
    positions = [(r,c) for r in range(9) for c in range(9)]
    random.shuffle(positions)

    removed = 0
    # 总格子数 = 81，目标移除数 = 81 - clues
    target_remove = max(0, 81 - max(17, min(81, clues)))  # 最少保留17
    for (r,c) in positions:
        if removed >= target_remove:
            break
        if puzzle[r][c] == 0: 
            continue
        # 暂存并移除
        backup = puzzle[r][c]
        puzzle[r][c] = 0

        # 如果需要对称挖空，可以同时挖对称位（这里用中心对称）
        symmetric_pos = None
        backup_sym = None
        if symmetric:
            sr, sc = 8 - r, 8 - c
            symmetric_pos = (sr, sc)
            if puzzle[sr][sc] != 0:
                backup_sym = puzzle[sr][sc]
                puzzle[sr][sc] = 0

        # 检查唯一解
        sol_count = count_solutions(puzzle, limit=2)
        if sol_count != 1:
            # 不唯一或无解，回退
            puzzle[r][c] = backup
            if symmetric and symmetric_pos and backup_sym is not None:
                sr, sc = symmetric_pos
                puzzle[sr][sc] = backup_sym
            continue

        # 成功移除
        removed += 1
        if symmetric and symmetric_pos and backup_sym is not None and (sr,sc) != (r,c):
            removed += 1  # 对称位也被移除

    return puzzle

# 生成器主函数：外部接口
def generate_sudoku(clues: int=30, symmetric: bool=False, seed: Optional[int]=None) -> Tuple[Grid, Grid]:
    """
    生成数独题目和它的完整解。
    clues: 保留数字个数（常见范围 17..40+；17 是最少线性唯一解数）
    symmetric: 是否尝试保持中心对称挖空
    seed: 随机种子（可选）
    返回 (puzzle, solution)
    """
    if seed is not None:
        random.seed(seed)
    # 初始空盘
    full = [[0]*9 for _ in range(9)]
    # 生成完整解盘
    ok = generate_full_grid(full)
    if not ok:
        raise RuntimeError("生成完整解失败，请重试（非常罕见）")
    solution = [row[:] for row in full]
    puzzle = make_puzzle_from_full(solution, clues=clues, symmetric=symmetric, random_seed=seed)
    return puzzle, solution

if __name__ == "__main__":
    for idx in range(100):
        puzzle, solution = generate_sudoku(clues=17+idx%10, symmetric=(idx%2==0), seed=idx)
        print(grid_to_string(puzzle))

# 交互方式
# 1. 点一下填数字
# 2. 双击填候选
# 3. 长按清除
# 4. 单指滑动：选中格子移动到邻近格子
