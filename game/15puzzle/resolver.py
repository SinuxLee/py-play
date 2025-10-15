import time
from collections import deque
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class PatternDatabase:
    """模式数据库：预计算部分拼图的精确解"""

    def __init__(self, pattern_tiles: List[int], size: int = 4):
        """
        :param pattern_tiles: 参与模式的数字列表，如[0,1,2,3]
        :param size: 拼图大小
        """
        self.pattern_tiles = set(pattern_tiles)
        self.size = size
        self.db = {}
        self._build_database()

    def _build_database(self):
        """使用BFS构建模式数据库"""
        print(f"构建模式数据库 {self.pattern_tiles}...", end=" ")
        start = time.time()

        # 目标状态（只关心pattern_tiles中的数字）
        goal = self._extract_pattern(tuple(range(16)))

        # BFS从目标状态反向搜索
        queue = deque([(goal, 0)])
        self.db[goal] = 0

        while queue:
            state, dist = queue.popleft()

            # 获取完整状态来生成后继
            full_state = self._expand_pattern(state)

            for next_full in self._get_neighbors_full(full_state):
                next_pattern = self._extract_pattern(next_full)
                if next_pattern not in self.db:
                    self.db[next_pattern] = dist + 1
                    queue.append((next_pattern, dist + 1))

        elapsed = time.time() - start
        print(f"完成！条目数: {len(self.db)}, 耗时: {elapsed:.2f}秒")

    def _extract_pattern(self, state: Tuple[int]) -> Tuple[int]:
        """从完整状态中提取模式"""
        return tuple(val if val in self.pattern_tiles else -1 for val in state)

    def _expand_pattern(self, pattern: Tuple[int]) -> Tuple[int]:
        """将模式扩展为完整状态（用于生成后继）"""
        result = []
        counter = 0
        for val in pattern:
            if val == -1:
                # 填充不在模式中的数字
                while counter in self.pattern_tiles:
                    counter += 1
                result.append(counter)
                counter += 1
            else:
                result.append(val)
        return tuple(result)

    def _get_neighbors_full(self, state: Tuple[int]) -> List[Tuple[int]]:
        """获取完整状态的所有后继"""
        zero_pos = state.index(0)
        zero_row, zero_col = divmod(zero_pos, self.size)
        neighbors = []

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = zero_row + dr, zero_col + dc
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                new_pos = new_row * self.size + new_col
                state_list = list(state)
                state_list[zero_pos], state_list[new_pos] = (
                    state_list[new_pos],
                    state_list[zero_pos],
                )
                neighbors.append(tuple(state_list))

        return neighbors

    def lookup(self, state: Tuple[int]) -> int:
        """查询状态到目标的距离"""
        pattern = self._extract_pattern(state)
        return self.db.get(pattern, 0)


class BidirectionalIDAstar:
    """双向IDA*搜索"""

    def __init__(self, initial: Tuple[int], goal: Tuple[int], heuristic_func):
        self.initial = initial
        self.goal = goal
        self.heuristic = heuristic_func
        self.size = 4
        self.nodes_explored = 0
        self.solution_found = False
        self.solution_path = []
        self.lock = threading.Lock()

    def _get_neighbors(self, state: Tuple[int], last_move: Optional[int] = None):
        """获取后继状态"""
        zero_pos = state.index(0)
        zero_row, zero_col = divmod(zero_pos, self.size)
        neighbors = []

        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for move_idx, (dr, dc) in enumerate(moves):
            if last_move is not None:
                if (
                    (move_idx == 0 and last_move == 1)
                    or (move_idx == 1 and last_move == 0)
                    or (move_idx == 2 and last_move == 3)
                    or (move_idx == 3 and last_move == 2)
                ):
                    continue

            new_row, new_col = zero_row + dr, zero_col + dc
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                new_pos = new_row * self.size + new_col
                state_list = list(state)
                state_list[zero_pos], state_list[new_pos] = (
                    state_list[new_pos],
                    state_list[zero_pos],
                )
                neighbors.append((tuple(state_list), move_idx))

        return neighbors

    def _search(
        self,
        state: Tuple[int],
        g: int,
        bound: int,
        path: List[int],
        forward_table: dict,
        backward_table: dict,
        is_forward: bool,
    ):
        """单向搜索"""
        with self.lock:
            if self.solution_found:
                return True, bound
            self.nodes_explored += 1

        h = self.heuristic(state)
        f = g + h

        if f > bound:
            return False, f

        # 检查是否在另一方向的搜索表中
        opposite_table = backward_table if is_forward else forward_table
        if state in opposite_table:
            # 找到交汇点
            with self.lock:
                if not self.solution_found:
                    self.solution_found = True
                    self.solution_path = path
            return True, bound

        # 转换表剪枝
        current_table = forward_table if is_forward else backward_table
        if state in current_table and current_table[state] <= g:
            return False, float("inf")
        current_table[state] = g

        min_next = float("inf")
        last_move = path[-1] if path else None

        for next_state, move in self._get_neighbors(state, last_move):
            path.append(move)
            found, next_bound = self._search(
                next_state,
                g + 1,
                bound,
                path,
                forward_table,
                backward_table,
                is_forward,
            )
            if found:
                return True, bound
            min_next = min(min_next, next_bound)
            path.pop()

        return False, min_next

    def solve(self, max_iterations: int = 50):
        """执行双向搜索"""
        bound_forward = self.heuristic(self.initial)
        bound_backward = self.heuristic(self.goal)

        for iteration in range(max_iterations):
            if self.solution_found:
                break

            forward_table = {}
            backward_table = {}
            path_forward = []
            path_backward = []

            # 前向搜索
            found_f, next_f = self._search(
                self.initial,
                0,
                bound_forward,
                path_forward,
                forward_table,
                backward_table,
                True,
            )

            if found_f:
                return self.solution_path

            # 后向搜索
            found_b, next_b = self._search(
                self.goal,
                0,
                bound_backward,
                path_backward,
                backward_table,
                forward_table,
                False,
            )

            if found_b:
                return self.solution_path

            bound_forward = next_f
            bound_backward = next_b

        return None


class AdvancedFifteenPuzzleSolver:
    """高级十五数码求解器 - 整合所有优化"""

    def __init__(self, initial_state: List[List[int]]):
        self.initial = self._flatten(initial_state)
        self.goal = tuple(range(16))
        self.size = 4
        self.moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.move_names = ["上", "下", "左", "右"]
        self.nodes_explored = 0

        # 预计算曼哈顿距离
        self._precompute_manhattan()

        # 构建模式数据库（分成多个小模式）
        print("\n初始化模式数据库...")
        self.pattern_dbs = [
            PatternDatabase([0, 1, 2, 3], 4),  # 第一行
            PatternDatabase([4, 5, 6, 7], 4),  # 第二行
            PatternDatabase([8, 9, 10, 11], 4),  # 第三行
        ]

    def _flatten(self, state: List[List[int]]) -> Tuple[int]:
        return tuple(val for row in state for val in row)

    def _to_2d(self, state: Tuple[int]) -> List[List[int]]:
        return [list(state[i : i + 4]) for i in range(0, 16, 4)]

    def _precompute_manhattan(self):
        self.manhattan_table = {}
        for num in range(16):
            self.manhattan_table[num] = {}
            goal_row, goal_col = divmod(num, 4)
            for pos in range(16):
                curr_row, curr_col = divmod(pos, 4)
                self.manhattan_table[num][pos] = abs(curr_row - goal_row) + abs(
                    curr_col - goal_col
                )

    def _manhattan_distance(self, state: Tuple[int]) -> int:
        distance = 0
        for pos, num in enumerate(state):
            if num != 0:
                distance += self.manhattan_table[num][pos]
        return distance

    def _linear_conflict(self, state: Tuple[int]) -> int:
        conflict = 0

        # 行冲突
        for row in range(4):
            for col1 in range(4):
                pos1 = row * 4 + col1
                tile1 = state[pos1]
                if tile1 == 0 or tile1 // 4 != row:
                    continue
                for col2 in range(col1 + 1, 4):
                    pos2 = row * 4 + col2
                    tile2 = state[pos2]
                    if tile2 == 0 or tile2 // 4 != row:
                        continue
                    if tile1 % 4 > tile2 % 4:
                        conflict += 2

        # 列冲突
        for col in range(4):
            for row1 in range(4):
                pos1 = row1 * 4 + col
                tile1 = state[pos1]
                if tile1 == 0 or tile1 % 4 != col:
                    continue
                for row2 in range(row1 + 1, 4):
                    pos2 = row2 * 4 + col
                    tile2 = state[pos2]
                    if tile2 == 0 or tile2 % 4 != col:
                        continue
                    if tile1 // 4 > tile2 // 4:
                        conflict += 2

        return conflict

    def _pattern_database_heuristic(self, state: Tuple[int]) -> int:
        """使用模式数据库的启发式（可采纳的）"""
        return max(db.lookup(state) for db in self.pattern_dbs)

    def _heuristic(self, state: Tuple[int]) -> int:
        """超强启发式：综合多种启发式的最大值"""
        h1 = self._manhattan_distance(state) + self._linear_conflict(state)
        h2 = self._pattern_database_heuristic(state)
        return max(h1, h2)

    def _get_neighbors(self, state: Tuple[int], last_move: Optional[int] = None):
        zero_pos = state.index(0)
        zero_row, zero_col = divmod(zero_pos, 4)
        neighbors = []

        for move_idx, (dr, dc) in enumerate(self.moves):
            if last_move is not None:
                if (
                    (move_idx == 0 and last_move == 1)
                    or (move_idx == 1 and last_move == 0)
                    or (move_idx == 2 and last_move == 3)
                    or (move_idx == 3 and last_move == 2)
                ):
                    continue

            new_row, new_col = zero_row + dr, zero_col + dc
            if 0 <= new_row < 4 and 0 <= new_col < 4:
                new_pos = new_row * 4 + new_col
                state_list = list(state)
                state_list[zero_pos], state_list[new_pos] = (
                    state_list[new_pos],
                    state_list[zero_pos],
                )
                neighbors.append((tuple(state_list), move_idx))

        return neighbors

    def _ida_search(
        self, state: Tuple[int], g: int, bound: int, path: List[int], trans_table: dict
    ) -> Tuple[bool, int]:
        self.nodes_explored += 1
        h = self._heuristic(state)
        f = g + h

        if f > bound:
            return False, f

        if h == 0:
            return True, f

        if state in trans_table and trans_table[state] <= g:
            return False, float("inf")
        trans_table[state] = g

        min_next = float("inf")
        last_move = path[-1] if path else None

        for next_state, move in self._get_neighbors(state, last_move):
            path.append(move)
            found, next_bound = self._ida_search(
                next_state, g + 1, bound, path, trans_table
            )

            if found:
                return True, bound

            min_next = min(min_next, next_bound)
            path.pop()

        return False, min_next

    def _is_solvable(self) -> bool:
        inversions = 0
        state = [x for x in self.initial if x != 0]

        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                if state[i] > state[j]:
                    inversions += 1

        zero_row = self.initial.index(0) // 4

        if (zero_row % 2 == 0 and inversions % 2 == 1) or (
            zero_row % 2 == 1 and inversions % 2 == 0
        ):
            return True
        return False

    def solve_parallel(self, num_workers: int = 4) -> Optional[List[str]]:
        """并行IDA*搜索：多个线程探索不同分支"""
        print("\n使用并行IDA*搜索...")
        print(f"工作线程数: {num_workers}")

        if not self._is_solvable():
            print("该问题无解！")
            return None

        start_time = time.time()
        bound = self._heuristic(self.initial)

        solution = [None]
        solution_lock = threading.Lock()

        def worker_search(worker_id: int, initial_moves: List[int]):
            """工作线程"""
            path = list(initial_moves)
            trans_table = {}

            # 从初始移动开始搜索
            state = self.initial
            g = 0
            for move in initial_moves:
                neighbors = self._get_neighbors(state)
                state = next(s for s, m in neighbors if m == move)
                g += 1

            found, _ = self._ida_search(state, g, bound, path, trans_table)

            if found:
                with solution_lock:
                    if solution[0] is None:
                        solution[0] = path

        # 获取初始的多个分支
        initial_neighbors = self._get_neighbors(self.initial)

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for i, (_, move) in enumerate(initial_neighbors):
                future = executor.submit(worker_search, i, [move])
                futures.append(future)

            for future in as_completed(futures):
                if solution[0] is not None:
                    break

        if solution[0]:
            elapsed = time.time() - start_time
            print(f"✓ 找到解！")
            print(f"  步数: {len(solution[0])}")
            print(f"  耗时: {elapsed:.3f} 秒")
            return [self.move_names[move] for move in solution[0]]

        return None

    def solve(self, method: str = "ida") -> Optional[List[str]]:
        """
        求解十五数码
        :param method: 'ida' (标准IDA*), 'bidirectional' (双向IDA*), 'parallel' (并行IDA*)
        """
        print("=" * 70)
        print("开始求解十五数码问题（高级版）")
        print("=" * 70)
        print("初始状态:")
        self._print_state(self.initial)

        if not self._is_solvable():
            print("该问题无解！")
            return None

        start_time = time.time()

        if method == "parallel":
            return self.solve_parallel()

        elif method == "bidirectional":
            print("\n使用双向IDA*搜索...")
            bidirectional = BidirectionalIDAstar(
                self.initial, self.goal, self._heuristic
            )
            path = bidirectional.solve()

            if path:
                elapsed = time.time() - start_time
                print(f"✓ 找到解！")
                print(f"  步数: {len(path)}")
                print(f"  探索节点: {bidirectional.nodes_explored}")
                print(f"  耗时: {elapsed:.3f} 秒")
                return [self.move_names[move] for move in path]
            return None

        else:  # 标准IDA*
            print(f"\n使用增强IDA*搜索（模式数据库 + 线性冲突）...")
            bound = self._heuristic(self.initial)
            path = []

            print(f"初始启发式估计: {bound} 步\n")

            iteration = 0
            while True:
                iteration += 1
                trans_table = {}
                nodes_before = self.nodes_explored

                print(f"迭代 {iteration}: 深度限制 = {bound}", end=" ")

                found, next_bound = self._ida_search(
                    self.initial, 0, bound, path, trans_table
                )

                nodes_this_iter = self.nodes_explored - nodes_before
                print(f"| 节点: {nodes_this_iter} | 表: {len(trans_table)}")

                if found:
                    elapsed = time.time() - start_time
                    print(f"\n✓ 找到解！")
                    print(f"  步数: {len(path)}")
                    print(f"  总探索节点: {self.nodes_explored}")
                    print(f"  耗时: {elapsed:.3f} 秒")
                    print(f"  速度: {self.nodes_explored/elapsed:.0f} 节点/秒")

                    return [self.move_names[move] for move in path]

                if next_bound == float("inf"):
                    return None

                bound = next_bound

    def _print_state(self, state: Tuple[int]):
        state_2d = self._to_2d(state)
        for row in state_2d:
            print(" ".join(f"{num:2d}" if num != 0 else " ." for num in row))
        print()


# 测试代码
if __name__ == "__main__":
    # 困难问题测试
    print("测试困难问题（约30-40步）")
    difficult_state = [[5, 1, 2, 4], [9, 6, 3, 8], [13, 15, 10, 11], [14, 0, 7, 12]]

    solver = AdvancedFifteenPuzzleSolver(difficult_state)

    # 方法1: 增强IDA*（模式数据库 + 线性冲突）
    print("\n" + "=" * 70)
    print("方法 1: 增强IDA*（模式数据库 + 线性冲突）")
    print("=" * 70)
    solution1 = solver.solve(method="ida")
    if solution1:
        print(
            f"\n解法: {' -> '.join(solution1[:10])}..."
            if len(solution1) > 10
            else f"\n解法: {' -> '.join(solution1)}"
        )

    # 重置节点计数器
    solver.nodes_explored = 0

    # 方法2: 双向IDA*
    print("\n" + "=" * 70)
    print("方法 2: 双向IDA*")
    print("=" * 70)
    solution2 = solver.solve(method="bidirectional")
    if solution2:
        print(
            f"\n解法: {' -> '.join(solution2[:10])}..."
            if len(solution2) > 10
            else f"\n解法: {' -> '.join(solution2)}"
        )

    # 简单测试
    print("\n\n" + "=" * 70)
    print("测试简单问题")
    print("=" * 70)
    simple_state = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 0, 15]]

    solver_simple = AdvancedFifteenPuzzleSolver(simple_state)
    solution = solver_simple.solve(method="ida")
    if solution:
        print(f"\n解法: {' -> '.join(solution)}")
