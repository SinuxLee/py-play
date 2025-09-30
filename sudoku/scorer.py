## 题目评分器
from typing import List, Tuple
from itertools import product, combinations

Grid = List[List[int]]

def print_grid(g: Grid):
    """打印数独网格"""
    for r in range(9):
        row = ""
        for c in range(9):
            v = g[r][c]
            row += "." if v == 0 else str(v)
            row += " "
            if c in (2,5): row += "| "
        print(row)
        if r in (2,5): print("-"*21)
    print()

def is_valid(g: Grid, r: int, c: int, v: int) -> bool:
    """检查在位置(r,c)放置数字v是否有效"""
    # 检查行
    if any(g[r][j] == v for j in range(9)): return False
    # 检查列
    if any(g[i][c] == v for i in range(9)): return False
    # 检查3x3宫格
    br, bc = (r//3)*3, (c//3)*3
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if g[i][j] == v:
                return False
    return True

def get_candidates(g: Grid) -> List[List[List[int]]]:
    """计算每个空格的候选数字"""
    cands = [[[] for _ in range(9)] for _ in range(9)]
    for r,c in product(range(9), repeat=2):
        if g[r][c] == 0:
            cands[r][c] = [v for v in range(1,10) if is_valid(g,r,c,v)]
    return cands

def update_candidates(g: Grid, cands: List[List[List[int]]], r: int, c: int, v: int):
    """当位置(r,c)确定为v时，更新所有相关候选数字"""
    # 清除该位置的候选数字
    cands[r][c] = []
    
    # 从同行、同列、同宫格中移除v
    for i in range(9):
        # 同行
        if v in cands[r][i]:
            cands[r][i].remove(v)
        # 同列
        if v in cands[i][c]:
            cands[i][c].remove(v)
    
    # 同宫格
    br, bc = (r//3)*3, (c//3)*3
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if v in cands[i][j]:
                cands[i][j].remove(v)

# ===== 基础技巧 =====

def apply_naked_single(g, cands, steps):
    """唯一候选数法 - 某个格子只有一个候选数字"""
    for r,c in product(range(9), repeat=2):
        if g[r][c]==0 and len(cands[r][c])==1:
            v = cands[r][c][0]
            g[r][c] = v
            update_candidates(g, cands, r, c, v)
            steps.append(f"Naked Single: ({r+1},{c+1}) = {v}")
            return True, 1
    return False, 0

def apply_hidden_single(g, cands, steps):
    """隐性唯一数 - 某个数字在行/列/宫格中只能放在一个位置"""
    # 检查行
    for r in range(9):
        for v in range(1,10):
            cells = [c for c in range(9) if g[r][c]==0 and v in cands[r][c]]
            if len(cells)==1:
                c = cells[0]
                g[r][c] = v
                update_candidates(g, cands, r, c, v)
                steps.append(f"Hidden Single (row): ({r+1},{c+1}) = {v}")
                return True, 2
    
    # 检查列
    for c in range(9):
        for v in range(1,10):
            cells = [r for r in range(9) if g[r][c]==0 and v in cands[r][c]]
            if len(cells)==1:
                r = cells[0]
                g[r][c] = v
                update_candidates(g, cands, r, c, v)
                steps.append(f"Hidden Single (col): ({r+1},{c+1}) = {v}")
                return True, 2
    
    # 检查宫格
    for box_r in range(3):
        for box_c in range(3):
            for v in range(1,10):
                cells = []
                for r in range(box_r*3, box_r*3+3):
                    for c in range(box_c*3, box_c*3+3):
                        if g[r][c]==0 and v in cands[r][c]:
                            cells.append((r,c))
                if len(cells)==1:
                    r, c = cells[0]
                    g[r][c] = v
                    update_candidates(g, cands, r, c, v)
                    steps.append(f"Hidden Single (box): ({r+1},{c+1}) = {v}")
                    return True, 2
    
    return False, 0

# ===== 中级技巧 =====

def apply_naked_pair(g, cands, steps):
    """裸对数 - 两个格子有相同的两个候选数字，可以从其他格子中排除这些数字"""
    # 检查行
    for r in range(9):
        pairs = [(c,tuple(sorted(cands[r][c]))) for c in range(9) if len(cands[r][c])==2 and g[r][c]==0]
        for i in range(len(pairs)):
            for j in range(i+1, len(pairs)):
                if pairs[i][1]==pairs[j][1]:
                    eliminated = False
                    for c in range(9):
                        if c not in (pairs[i][0], pairs[j][0]) and g[r][c]==0:
                            before_len = len(cands[r][c])
                            cands[r][c] = [x for x in cands[r][c] if x not in pairs[i][1]]
                            if len(cands[r][c]) < before_len:
                                eliminated = True
                    if eliminated:
                        steps.append(f"Naked Pair (row {r+1}): cells ({r+1},{pairs[i][0]+1}) and ({r+1},{pairs[j][0]+1}) = {pairs[i][1]}")
                        return True, 3
    
    # 检查列
    for c in range(9):
        pairs = [(r,tuple(sorted(cands[r][c]))) for r in range(9) if len(cands[r][c])==2 and g[r][c]==0]
        for i in range(len(pairs)):
            for j in range(i+1, len(pairs)):
                if pairs[i][1]==pairs[j][1]:
                    eliminated = False
                    for r in range(9):
                        if r not in (pairs[i][0], pairs[j][0]) and g[r][c]==0:
                            before_len = len(cands[r][c])
                            cands[r][c] = [x for x in cands[r][c] if x not in pairs[i][1]]
                            if len(cands[r][c]) < before_len:
                                eliminated = True
                    if eliminated:
                        steps.append(f"Naked Pair (col {c+1}): cells ({pairs[i][0]+1},{c+1}) and ({pairs[j][0]+1},{c+1}) = {pairs[i][1]}")
                        return True, 3
    
    return False, 0

def apply_pointing_pair(g, cands, steps):
    """宫格行列排除 - 如果某个数字在宫格中只能出现在同一行或同一列，则可以从该行或列的其他宫格中排除"""
    for box_r in range(3):
        for box_c in range(3):
            for v in range(1, 10):
                # 找到该宫格中包含数字v的所有位置
                positions = []
                for r in range(box_r*3, box_r*3+3):
                    for c in range(box_c*3, box_c*3+3):
                        if g[r][c] == 0 and v in cands[r][c]:
                            positions.append((r, c))
                
                if len(positions) >= 2:
                    # 检查是否都在同一行
                    if len(set(pos[0] for pos in positions)) == 1:
                        row = positions[0][0]
                        eliminated = False
                        for c in range(9):
                            if c < box_c*3 or c >= box_c*3+3:  # 不在当前宫格
                                if g[row][c] == 0 and v in cands[row][c]:
                                    cands[row][c].remove(v)
                                    eliminated = True
                        if eliminated:
                            steps.append(f"Pointing Pair: digit {v} in box ({box_r+1},{box_c+1}) eliminates from row {row+1}")
                            return True, 4
                    
                    # 检查是否都在同一列
                    if len(set(pos[1] for pos in positions)) == 1:
                        col = positions[0][1]
                        eliminated = False
                        for r in range(9):
                            if r < box_r*3 or r >= box_r*3+3:  # 不在当前宫格
                                if g[r][col] == 0 and v in cands[r][col]:
                                    cands[r][col].remove(v)
                                    eliminated = True
                        if eliminated:
                            steps.append(f"Pointing Pair: digit {v} in box ({box_r+1},{box_c+1}) eliminates from col {col+1}")
                            return True, 4
    
    return False, 0

def apply_box_line_reduction(g, cands, steps):
    """宫格排除 - 如果某个数字在行或列中只能出现在某个宫格内，则可以从该宫格的其他位置排除"""
    # 检查行
    for r in range(9):
        for v in range(1, 10):
            positions = [c for c in range(9) if g[r][c] == 0 and v in cands[r][c]]
            if len(positions) >= 2:
                # 检查是否都在同一个宫格
                boxes = set(c // 3 for c in positions)
                if len(boxes) == 1:
                    box_c = positions[0] // 3
                    box_r = r // 3
                    eliminated = False
                    for br in range(box_r*3, box_r*3+3):
                        for bc in range(box_c*3, box_c*3+3):
                            if br != r and g[br][bc] == 0 and v in cands[br][bc]:
                                cands[br][bc].remove(v)
                                eliminated = True
                    if eliminated:
                        steps.append(f"Box-Line Reduction: digit {v} in row {r+1} eliminates from box ({box_r+1},{box_c+1})")
                        return True, 4
    
    # 检查列
    for c in range(9):
        for v in range(1, 10):
            positions = [r for r in range(9) if g[r][c] == 0 and v in cands[r][c]]
            if len(positions) >= 2:
                # 检查是否都在同一个宫格
                boxes = set(r // 3 for r in positions)
                if len(boxes) == 1:
                    box_r = positions[0] // 3
                    box_c = c // 3
                    eliminated = False
                    for br in range(box_r*3, box_r*3+3):
                        for bc in range(box_c*3, box_c*3+3):
                            if bc != c and g[br][bc] == 0 and v in cands[br][bc]:
                                cands[br][bc].remove(v)
                                eliminated = True
                    if eliminated:
                        steps.append(f"Box-Line Reduction: digit {v} in col {c+1} eliminates from box ({box_r+1},{box_c+1})")
                        return True, 4
    
    return False, 0

def apply_naked_triple(g, cands, steps):
    """裸三数组 - 三个格子共同拥有相同的三个候选数字"""
    # 检查行
    for r in range(9):
        cells = [(c, tuple(sorted(cands[r][c]))) for c in range(9) if 2 <= len(cands[r][c]) <= 3 and g[r][c] == 0]
        for combo in combinations(cells, 3):
            all_values = set()
            for _, values in combo:
                all_values.update(values)
            if len(all_values) == 3:
                eliminated = False
                for c in range(9):
                    if c not in [cell[0] for cell in combo] and g[r][c] == 0:
                        before_len = len(cands[r][c])
                        cands[r][c] = [x for x in cands[r][c] if x not in all_values]
                        if len(cands[r][c]) < before_len:
                            eliminated = True
                if eliminated:
                    cols = [cell[0]+1 for cell in combo]
                    steps.append(f"Naked Triple (row {r+1}): cells {cols} = {sorted(all_values)}")
                    return True, 5
    
    return False, 0

# ===== 高级技巧 =====

def apply_xwing(g, cands, steps):
    """X-Wing 模式 - 在两行（或两列）中，某个数字只能出现在相同的两列（或两行）中"""
    # 检查行中的X-Wing
    for v in range(1, 10):
        row_positions = {}
        for r in range(9):
            cols = [c for c in range(9) if g[r][c] == 0 and v in cands[r][c]]
            if len(cols) == 2:
                key = tuple(cols)
                if key not in row_positions:
                    row_positions[key] = []
                row_positions[key].append(r)
        
        for cols, rows in row_positions.items():
            if len(rows) == 2:
                # 找到X-Wing，从这两列的其他行中排除该数字
                eliminated = False
                for r in range(9):
                    if r not in rows:
                        for c in cols:
                            if g[r][c] == 0 and v in cands[r][c]:
                                cands[r][c].remove(v)
                                eliminated = True
                if eliminated:
                    steps.append(f"X-Wing: digit {v} in rows {[r+1 for r in rows]} cols {[c+1 for c in cols]}")
                    return True, 6
    
    # 检查列中的X-Wing
    for v in range(1, 10):
        col_positions = {}
        for c in range(9):
            rows = [r for r in range(9) if g[r][c] == 0 and v in cands[r][c]]
            if len(rows) == 2:
                key = tuple(rows)
                if key not in col_positions:
                    col_positions[key] = []
                col_positions[key].append(c)
        
        for rows, cols in col_positions.items():
            if len(cols) == 2:
                # 找到X-Wing，从这两行的其他列中排除该数字
                eliminated = False
                for c in range(9):
                    if c not in cols:
                        for r in rows:
                            if g[r][c] == 0 and v in cands[r][c]:
                                cands[r][c].remove(v)
                                eliminated = True
                if eliminated:
                    steps.append(f"X-Wing: digit {v} in cols {[c+1 for c in cols]} rows {[r+1 for r in rows]}")
                    return True, 6
    
    return False, 0

def apply_swordfish(g, cands, steps):
    """Swordfish 模式 - X-Wing的扩展，涉及三行三列"""
    # 检查行中的Swordfish
    for v in range(1, 10):
        row_positions = {}
        for r in range(9):
            cols = [c for c in range(9) if g[r][c] == 0 and v in cands[r][c]]
            if 2 <= len(cols) <= 3:
                key = tuple(sorted(cols))
                if key not in row_positions:
                    row_positions[key] = []
                row_positions[key].append(r)
        
        # 寻找三行三列的组合
        for cols, rows in row_positions.items():
            if len(rows) == 3 and len(cols) == 3:
                # 验证这确实形成Swordfish（每行最多在这三列中有候选数字）
                valid_swordfish = True
                for r in rows:
                    row_cols = [c for c in range(9) if g[r][c] == 0 and v in cands[r][c]]
                    if not set(row_cols).issubset(set(cols)):
                        valid_swordfish = False
                        break
                
                if valid_swordfish:
                    # 从这三列的其他行中排除该数字
                    eliminated = False
                    for r in range(9):
                        if r not in rows:
                            for c in cols:
                                if g[r][c] == 0 and v in cands[r][c]:
                                    cands[r][c].remove(v)
                                    eliminated = True
                    if eliminated:
                        steps.append(f"Swordfish: digit {v} in rows {[r+1 for r in rows]} cols {[c+1 for c in cols]}")
                        return True, 7
    
    # 检查列中的Swordfish
    for v in range(1, 10):
        col_positions = {}
        for c in range(9):
            rows = [r for r in range(9) if g[r][c] == 0 and v in cands[r][c]]
            if 2 <= len(rows) <= 3:
                key = tuple(sorted(rows))
                if key not in col_positions:
                    col_positions[key] = []
                col_positions[key].append(c)
        
        # 寻找三列三行的组合
        for rows, cols in col_positions.items():
            if len(cols) == 3 and len(rows) == 3:
                # 验证这确实形成Swordfish
                valid_swordfish = True
                for c in cols:
                    col_rows = [r for r in range(9) if g[r][c] == 0 and v in cands[r][c]]
                    if not set(col_rows).issubset(set(rows)):
                        valid_swordfish = False
                        break
                
                if valid_swordfish:
                    # 从这三行的其他列中排除该数字
                    eliminated = False
                    for c in range(9):
                        if c not in cols:
                            for r in rows:
                                if g[r][c] == 0 and v in cands[r][c]:
                                    cands[r][c].remove(v)
                                    eliminated = True
                    if eliminated:
                        steps.append(f"Swordfish: digit {v} in cols {[c+1 for c in cols]} rows {[r+1 for r in rows]}")
                        return True, 7
    
    return False, 0

def apply_xywing(g, cands, steps):
    """XY-Wing 模式"""
    # 寻找pivot点（有两个候选数字的格子）
    for r in range(9):
        for c in range(9):
            if g[r][c] == 0 and len(cands[r][c]) == 2:
                pivot_cands = set(cands[r][c])
                # 寻找pincers（与pivot共享一行或一列，且有两个候选数字）
                pincers = []
                
                # 同行的pincers
                for c2 in range(9):
                    if c2 != c and g[r][c2] == 0 and len(cands[r][c2]) == 2:
                        if len(set(cands[r][c2]).intersection(pivot_cands)) == 1:
                            pincers.append((r, c2, set(cands[r][c2])))
                
                # 同列的pincers
                for r2 in range(9):
                    if r2 != r and g[r2][c] == 0 and len(cands[r2][c]) == 2:
                        if len(set(cands[r2][c]).intersection(pivot_cands)) == 1:
                            pincers.append((r2, c, set(cands[r2][c])))
                
                # 检查是否形成XY-Wing
                for i, (r1, c1, cands1) in enumerate(pincers):
                    for j, (r2, c2, cands2) in enumerate(pincers[i+1:], i+1):
                        common_with_pivot1 = pivot_cands.intersection(cands1)
                        common_with_pivot2 = pivot_cands.intersection(cands2)
                        
                        if (len(common_with_pivot1) == 1 and len(common_with_pivot2) == 1 and 
                            common_with_pivot1 != common_with_pivot2):
                            # 找到了XY-Wing
                            remaining1 = cands1 - common_with_pivot1
                            remaining2 = cands2 - common_with_pivot2
                            
                            if remaining1 == remaining2 and len(remaining1) == 1:
                                target_digit = list(remaining1)[0]
                                # 从能同时看到两个pincers的格子中排除target_digit
                                eliminated = False
                                for rr in range(9):
                                    for cc in range(9):
                                        if (g[rr][cc] == 0 and target_digit in cands[rr][cc] and
                                            ((rr == r1 or cc == c1) and (rr == r2 or cc == c2)) and
                                            (rr, cc) not in [(r, c), (r1, c1), (r2, c2)]):
                                            cands[rr][cc].remove(target_digit)
                                            eliminated = True
                                
                                if eliminated:
                                    steps.append(f"XY-Wing: pivot ({r+1},{c+1}), pincers ({r1+1},{c1+1}) ({r2+1},{c2+1})")
                                    return True, 8
    
    return False, 0

def apply_simple_coloring(g, cands, steps):
    """简单着色法"""
    for v in range(1, 10):
        # 找到所有只有两个候选位置的单元（强链接）
        strong_links = []
        
        # 检查行
        for r in range(9):
            positions = [c for c in range(9) if g[r][c] == 0 and v in cands[r][c]]
            if len(positions) == 2:
                strong_links.append(((r, positions[0]), (r, positions[1])))
        
        # 检查列
        for c in range(9):
            positions = [r for r in range(9) if g[r][c] == 0 and v in cands[r][c]]
            if len(positions) == 2:
                strong_links.append(((positions[0], c), (positions[1], c)))
        
        # 检查宫格
        for box_r in range(3):
            for box_c in range(3):
                positions = []
                for r in range(box_r*3, box_r*3+3):
                    for c in range(box_c*3, box_c*3+3):
                        if g[r][c] == 0 and v in cands[r][c]:
                            positions.append((r, c))
                if len(positions) == 2:
                    strong_links.append((positions[0], positions[1]))
        
        if strong_links:
            # 构建着色图并寻找矛盾
            # 这里给出简化实现
            pass
    
    return False, 0

# ===== 主求解器 =====
def solve_with_logic(grid: Grid):
    """使用逻辑技巧求解数独"""
    g = [row[:] for row in grid]
    steps = []
    hardest = 0
    max_iterations = 1000  # 防止无限循环
    iteration = 0
    
    strategies = [
        apply_naked_single,         # 1 - 唯一候选数
        apply_hidden_single,        # 2 - 隐性唯一数
        apply_naked_pair,           # 3 - 裸对数
        #apply_hidden_pair,          # 4 - 隐性对数
        apply_pointing_pair,        # 4 - 指向对数
        apply_box_line_reduction,   # 4 - 宫格排除
        apply_naked_triple,         # 5 - 裸三数组
        apply_xwing,               # 6 - X-Wing
        apply_swordfish,           # 7 - 剑鱼
        apply_xywing,              # 8 - XY-Wing
        #apply_xyzw,                # 9 - XYZ-Wing
        #apply_unique_rectangle,     # 10 - 唯一矩形
        apply_simple_coloring,      # 11 - 简单着色法
    ]
    
    while iteration < max_iterations:
        iteration += 1
        
        # 检查是否已完成
        if all(all(cell != 0 for cell in row) for row in g):
            return True, hardest, steps
        
        # 重新计算候选数字
        cands = get_candidates(g)
        
        # 检查是否有空格没有候选数字（无解）
        for r in range(9):
            for c in range(9):
                if g[r][c] == 0 and len(cands[r][c]) == 0:
                    return False, hardest, steps + [f"No solution: cell ({r+1},{c+1}) has no candidates"]
        
        # 尝试应用策略
        progress_made = False
        for strat in strategies:
            changed, level = strat(g, cands, steps)
            if changed:
                hardest = max(hardest, level)
                progress_made = True
                break
        
        if not progress_made:
            # 没有策略能继续，可能需要更高级的技巧或猜测
            break
    
    # 检查是否完成
    completed = all(all(cell != 0 for cell in row) for row in g)
    return completed, hardest, steps

def difficulty_label(level: int) -> str:
    """根据技巧等级返回难度标签"""
    if level <= 2:
        return "Easy"
    elif level <= 4:
        return "Medium"
    elif level <= 6:
        return "Hard"
    elif level <= 8:
        return "Expert"
    else:
        return "Master"

def validate_solution(grid: Grid) -> bool:
    """验证数独解是否正确"""
    # 检查每行
    for r in range(9):
        if set(grid[r]) != set(range(1, 10)):
            return False
    
    # 检查每列
    for c in range(9):
        if set(grid[r][c] for r in range(9)) != set(range(1, 10)):
            return False
    
    # 检查每个宫格
    for box_r in range(3):
        for box_c in range(3):
            box_nums = []
            for r in range(box_r*3, box_r*3+3):
                for c in range(box_c*3, box_c*3+3):
                    box_nums.append(grid[r][c])
            if set(box_nums) != set(range(1, 10)):
                return False
    
    return True
        
def get_puzzle_statistics(grid: Grid) -> dict:
    """获取数独的统计信息"""
    filled_count = sum(1 for r in range(9) for c in range(9) if grid[r][c] != 0)
    empty_count = 81 - filled_count
    
    # 计算每行、每列、每宫格的填充数量
    row_counts = [sum(1 for c in range(9) if grid[r][c] != 0) for r in range(9)]
    col_counts = [sum(1 for r in range(9) if grid[r][c] != 0) for c in range(9)]
    
    box_counts = []
    for box_r in range(3):
        for box_c in range(3):
            count = 0
            for r in range(box_r*3, box_r*3+3):
                for c in range(box_c*3, box_c*3+3):
                    if grid[r][c] != 0:
                        count += 1
            box_counts.append(count)
    
    return {
        'filled_cells': filled_count,
        'empty_cells': empty_count,
        'fill_rate': filled_count / 81 * 100,
        'min_row_filled': min(row_counts),
        'max_row_filled': max(row_counts),
        'min_col_filled': min(col_counts),
        'max_col_filled': max(col_counts),
        'min_box_filled': min(box_counts),
        'max_box_filled': max(box_counts),
    }

def print_detailed_analysis(puzzle, solved, level, steps, final_grid=None):
    """打印详细的分析结果"""
    stats = get_puzzle_statistics(puzzle)
    
    print(f"📊 数独统计:")
    print(f"   已填充格子: {stats['filled_cells']}/81 ({stats['fill_rate']:.1f}%)")
    print(f"   行填充范围: {stats['min_row_filled']}-{stats['max_row_filled']}")
    print(f"   列填充范围: {stats['min_col_filled']}-{stats['max_col_filled']}")
    print(f"   宫格填充范围: {stats['min_box_filled']}-{stats['max_box_filled']}")
    
    print(f"\n🎯 求解结果: {'✅ 成功' if solved else '❌ 失败'}")
    print(f"📈 最高技巧等级: {level} → {difficulty_label(level)}")
    print(f"🔧 使用步骤数: {len(steps)}")
    
    if steps:
        # 统计使用的技巧
        technique_counts = {}
        for step in steps:
            technique = step.split(':')[0]
            technique_counts[technique] = technique_counts.get(technique, 0) + 1
        
        print(f"\n🛠️  使用的技巧:")
        for technique, count in sorted(technique_counts.items()):
            print(f"   {technique}: {count}次")
        
        print(f"\n📝 详细步骤 (前15步):")
        for j, step in enumerate(steps[:15], 1):
            print(f"   {j:2d}. {step}")
        
        if len(steps) > 15:
            print(f"   ... (还有{len(steps)-15}步)")
    
    if solved and final_grid:
        print(f"\n✅ 解的正确性: {'正确' if validate_solution(final_grid) else '错误'}")
    
    print("-" * 60)
    
def parse_sudoku_line(line: str) -> Grid:
    """
    将一行数独字符串解析为 9x9 的二维数组
    例如:
    8.17..4..;...1...25;2...3..7.;3......52;....9....;69......3;.4..1...7;75...2...;..8..45.6
    """
    # 按分号分割成 9 行
    rows = line.strip().split(";")
    if len(rows) != 9:
        raise ValueError("每行数独必须包含 9 个分号分隔的部分")

    sudoku: Grid = []
    for r in rows:
        if len(r) != 9:
            raise ValueError(f"数独每行必须 9 个字符: {r}")
        row = [int(c) if c.isdigit() else 0 for c in r]  # '.' -> 0
        sudoku.append(row)
    return sudoku


def read_sudoku_file(filename: str) -> List[Grid]:
    """
    从文件读取所有数独，返回一个列表，每个元素是 9x9 的二维数组
    """
    sudokus: list[Grid] = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            sudokus.append(parse_sudoku_line(line))
    return sudokus


# 示例用法
if __name__ == "__main__":
    filename = "puzzle.txt"
    all_sudokus = read_sudoku_file(filename)
    for i,puzzle in enumerate(all_sudokus, 1):
        print(f"=== test case {i} ===")
        # print("puzzle:")
        # print_grid(puzzle)
        
        solved, level, steps = solve_with_logic(puzzle)
        print(f"Solved: {solved}, Difficulty Level: {level} ({difficulty_label(level)})")
