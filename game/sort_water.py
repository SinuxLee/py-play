from enum import Enum, auto, unique
from heapq import heappush, heappop
import random
from copy import deepcopy
import time
import json

random.seed(time.time())


@unique
class COLOR(Enum):
    RED = auto()
    BLUE = auto()
    GREE = auto()
    ORANGE = auto()
    PERPLE = auto()
    CYAN = auto()
    YELLOW = auto()
    GRAY = auto()
    MAX = auto()


capacity = 4  # 每个瓶子的容量
bottle_amount = 19  # 瓶子总数
empty_bottle = 2  # 两个空瓶


class WaterSortSolver:
    def __init__(self,  max_capacity=4):
        self.max_capacity = max_capacity

    def _count_colors(self):
        """统计每种颜色的总数"""
        color_count: dict[int, int] = {}
        for bottle in self.initial_state:
            for color in bottle:
                color_count[color] = color_count.get(color, 0) + 1
        return color_count

    def change_puzzle(self, bottles: list[list[int]]):
        self.initial_state = [list(b) for b in bottles]
        self.color_count = self._count_colors()

    def gen_some_valid_puzzle(self, count: int = 100):
        for _ in range(count):
            puzzle = self.gen_new_puzzle()
            self.change_puzzle(puzzle)
            solution = self.solve(max_steps=10000, time_limit=3)
            if not solution:
                continue
            
            print(json.dumps(puzzle))

    def gen_new_puzzle(self) -> list[list[int]]:
        color_blocks: list[int] = []
        for _ in range(bottle_amount-empty_bottle):
            color = random.randint(COLOR.RED.value, COLOR.MAX.value)
            color_blocks.extend([color for _ in range(capacity)])

        random.shuffle(color_blocks)
        bottles: list[list[int]] = [[] for _ in range(bottle_amount)]
        for idx, b in enumerate(bottles):
            count = capacity//2 if idx < 2 else capacity
            b.extend(color_blocks[:count])
            color_blocks = color_blocks[count:]

        return bottles

    def get_top_color_count(self, bottle: list[int]):
        """获取瓶子顶部相同颜色的数量"""
        if not bottle:
            return None, 0

        color = bottle[-1]
        count = 0
        for i in range(len(bottle) - 1, -1, -1):
            if bottle[i] == color:
                count += 1
            else:
                break
        return color, count

    def is_bottle_complete(self, bottle: list[int]):
        """检查单个瓶子是否已完成"""
        return len(bottle) == self.max_capacity and len(set(bottle)) == 1

    def is_bottle_single_color(self, bottle: list[int]):
        """检查瓶子是否只有一种颜色（但可能未满）"""
        return len(bottle) > 0 and len(set(bottle)) == 1

    def count_complete_bottles(self, bottles: list[list[int]]):
        """统计已完成的瓶子数"""
        return sum(1 for b in bottles if self.is_bottle_complete(b))

    def is_valid_pour(self, from_bottle: list[int], to_bottle: list[int]):
        """检查倒水是否合法"""
        if not from_bottle or len(to_bottle) >= self.max_capacity:
            return False

        if not to_bottle:
            return True

        if from_bottle[-1] != to_bottle[-1]:
            return False

        return True

    def is_useful_move(self, state, from_idx: int, to_idx: int):
        """判断这次移动是否有意义 - 强化版剪枝"""
        from_bottle = state[from_idx]
        to_bottle = state[to_idx]

        # 1. 不要从完成的瓶子倒出
        if self.is_bottle_complete(from_bottle):
            return False

        # 2. 不要倒入完成的瓶子
        if self.is_bottle_complete(to_bottle):
            return False

        # 3. 如果源瓶子只有一种颜色且目标是空瓶，只在有必要时才倒
        if not to_bottle and self.is_bottle_single_color(from_bottle):
            # 只有当源瓶子未满时才考虑倒入空瓶
            if len(from_bottle) == self.max_capacity:
                return False

        # 4. 不要在两个单色瓶子之间来回倒
        if self.is_bottle_single_color(from_bottle) and self.is_bottle_single_color(to_bottle):
            if from_bottle[-1] == to_bottle[-1]:
                # 只有在能完成目标瓶子时才倒
                from_color, from_count = self.get_top_color_count(from_bottle)
                total = len(to_bottle) + from_count
                if total < self.max_capacity:
                    return False

        # 5. 避免把已排序好的部分打乱
        if to_bottle and len(to_bottle) >= 2:
            # 如果目标瓶子底部已经是同色的，不要轻易倒入
            bottom_color = to_bottle[0]
            is_bottom_sorted = all(c == bottom_color for c in to_bottle)
            if is_bottom_sorted and from_bottle[-1] != bottom_color:
                return False

        return True

    def pour_water(self, bottles: list[list[int]], from_idx: int, to_idx: int):
        """执行倒水操作"""
        new_bottles = deepcopy(bottles)
        from_bottle = new_bottles[from_idx]
        to_bottle = new_bottles[to_idx]

        color = from_bottle[-1]
        count = 0

        while (from_bottle and
               from_bottle[-1] == color and
               len(to_bottle) < self.max_capacity):
            to_bottle.append(from_bottle.pop())
            count += 1

        return new_bottles, count

    def is_solved(self, bottles: list[list[int]]):
        """检查是否完成"""
        for bottle in bottles:
            if not bottle:
                continue
            if len(bottle) != self.max_capacity or len(set(bottle)) != 1:
                return False
        return True

    def state_to_tuple(self, bottles: list[list[int]]):
        """将状态转换为元组用于哈希"""
        return tuple(tuple(b) for b in bottles)

    def get_heuristic(self, bottles: list[list[int]]):
        """改进的启发式函数"""
        h = 0

        # 统计当前每种颜色的分布
        color_bottles: dict[int, list[int]] = {}  # 每种颜色在哪些瓶子里
        for i, bottle in enumerate(bottles):
            for color in set(bottle):
                if color not in color_bottles:
                    color_bottles[color] = []
                color_bottles[color].append(i)

        # 对每种颜色计算代价
        for color, bottle_indices in color_bottles.items():
            # 颜色分散在多个瓶子中，代价更高
            h += (len(bottle_indices) - 1) * 2

            # 检查每个包含该颜色的瓶子
            for idx in bottle_indices:
                bottle = bottles[idx]
                if self.is_bottle_complete(bottle):
                    continue

                # 如果不在顶部，需要额外移动
                top_color, _ = self.get_top_color_count(bottle)
                if top_color != color:
                    # 计算该颜色上面有多少层
                    layers_above = 0
                    for i in range(len(bottle) - 1, -1, -1):
                        if bottle[i] == color:
                            break
                        layers_above += 1
                    h += layers_above

        # 未完成的瓶子数
        incomplete = sum(
            1 for b in bottles if b and not self.is_bottle_complete(b))
        h += incomplete * 0.5

        return h

    def get_priority_moves(self, state):
        """获取优先级排序的移动列表 - 更智能的排序"""
        moves = []

        for i in range(len(state)):
            if not state[i] or self.is_bottle_complete(state[i]):
                continue

            from_color, from_count = self.get_top_color_count(state[i])

            for j in range(len(state)):
                if i == j:
                    continue

                if not self.is_valid_pour(state[i], state[j]):
                    continue

                if not self.is_useful_move(state, i, j):
                    continue

                # 计算优先级
                priority = 0

                to_color, to_count = self.get_top_color_count(state[j])
                can_pour = min(from_count, self.max_capacity - len(state[j]))

                # 最高优先级：能完成一个瓶子
                if to_color == from_color:
                    total = len(state[j]) + can_pour
                    if total == self.max_capacity:
                        priority += 1000
                    elif total > self.max_capacity * 0.75:
                        priority += 500

                # 高优先级：能清空源瓶子
                if len(state[i]) == from_count:
                    priority += 300

                # 中高优先级：倒入已有相同颜色的瓶子
                if state[j] and to_color == from_color:
                    priority += 200

                # 中优先级：倒入空瓶
                if not state[j]:
                    # 但如果源瓶子是单色的且满了，优先级降低
                    if self.is_bottle_single_color(state[i]) and len(state[i]) == self.max_capacity:
                        priority += 10
                    else:
                        priority += 150

                # 根据能倒的数量加分
                priority += can_pour * 10

                # 如果源瓶子只剩这一种颜色，优先级提高
                if self.is_bottle_single_color(state[i]):
                    priority += 100

                moves.append((priority, i, j))

        # 按优先级排序
        moves.sort(reverse=True)
        return [(i, j) for _, i, j in moves]

    def solve(self, max_steps=500000, time_limit=300):
        """使用A*算法求解，增加时间和步数限制"""

        start_time = time.time()

        initial_h = self.get_heuristic(self.initial_state)
        heap = [(initial_h, 0, self.initial_state, [])]
        visited = {self.state_to_tuple(self.initial_state)}

        steps = 0
        max_queue_size = 0
        best_complete = 0

        while heap:
            steps += 1
            max_queue_size = max(max_queue_size, len(heap))

            # 检查时间限制
            elapsed = time.time() - start_time
            if elapsed > time_limit:
                return None

            # 检查步数限制
            if steps > max_steps:
                return None

            _, cost, current_state, path = heappop(heap)
            # 检查是否完成
            if self.is_solved(current_state):
                elapsed = time.time() - start_time
                return path

            # 跟踪最佳状态
            complete = self.count_complete_bottles(current_state)
            if complete > best_complete:
                best_complete = complete

            # 生成后继状态
            priority_moves = self.get_priority_moves(current_state)

            # 限制分支因子，只探索前N个最优移动
            for i, j in priority_moves[:15]:  # 只取前15个最优移动
                new_state, count = self.pour_water(current_state, i, j)
                state_tuple = self.state_to_tuple(new_state)

                if state_tuple not in visited:
                    visited.add(state_tuple)
                    new_cost = cost + 1
                    h = self.get_heuristic(new_state)
                    f = new_cost + h
                    new_path = path + [(i, j, count)]
                    heappush(heap, (f, new_cost, new_state, new_path))

        return None

    def print_solution(self, solution, verbose=True):
        """打印解决方案"""
        if solution is None:
            return

        print(f"\n{'='*70}")
        print(f"找到解决方案，共需 {len(solution)} 步")
        print(f"{'='*70}\n")

        if not verbose and len(solution) > 20:
            print("(解决方案较长，仅显示关键步骤)\n")

        state = deepcopy(self.initial_state)

        if verbose:
            print("初始状态：")
            self.print_state(state)
            print()

        for step_num, (from_idx, to_idx, count) in enumerate(solution, 1):
            state, _ = self.pour_water(state, from_idx, to_idx)

            if verbose or len(solution) <= 20:
                print(f"步骤 {step_num}: 瓶子 {from_idx} → 瓶子 {to_idx} ({count}份)")
                if verbose:
                    self.print_state(state)
                    print()
            elif step_num % 10 == 0 or step_num == len(solution):
                print(f"步骤 {step_num}: 瓶子 {from_idx} → 瓶子 {to_idx} ({count}份)")

        if not verbose:
            print("\n最终状态：")
            self.print_state(state)

    def print_state(self, bottles):
        return
        """打印当前状态"""
        for i, bottle in enumerate(bottles):
            status = " ✓" if self.is_bottle_complete(bottle) else ""
            print(f"瓶子 {i:2d}: {bottle}{status}")


solver = WaterSortSolver()
solver.gen_some_valid_puzzle()
