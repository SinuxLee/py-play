"""
旅行商问题(Travelling Salesman Problem)
给定一组城市以及每两座城市之间的距离，要求找到一条最短的闭合路径
"""

# 用 Python 同时运行 模拟退火 (Simulated Annealing) 和 遗传算法 (Genetic Algorithm) 求解
# 我将生成一个固定的 20 个城市的实例（带坐标），然后分别用两个算法求近似最短环路并绘图展示结果。
# 注意：为可复现性，设定了随机种子。

import random
import math
import time
from copy import deepcopy
import matplotlib.pyplot as plt

# 固定随机种子以便复现
RND_SEED = 42
random.seed(RND_SEED)

# 生成 20 个城市
N = 20
postions: list[tuple[float, float]] = [
    (random.uniform(0, 100), random.uniform(0, 100)) for _ in range(N)
]

# 给城市编号
cities: list[tuple[int, float, float]] = [
    (i, x, y) for i, (x, y) in enumerate(postions)
]


# 计算距离矩阵
def euclidean(a: tuple[int, float, float], b: tuple[int, float, float]):
    return math.hypot(a[1] - b[1], a[2] - b[2])


dist: list[list[float]] = [[0.0] * N for _ in range(N)]
for i in range(N):
    for j in range(N):
        dist[i][j] = euclidean(cities[i], cities[j])


# 路径长度计算, 计算一次旅程
def path_length(tour: list[int]):
    L = 0.0
    for i in range(len(tour) - 1):
        L += dist[tour[i]][tour[i + 1]]
    L += dist[tour[-1]][tour[0]]
    return L


# ------------------------------------------------------
# 模拟退火（Simulated Annealing）实现（2-opt 邻域）
# ------------------------------------------------------


def two_opt_swap(route, i, k):
    """
    随机一个切片，翻转切片后重新组成一个整体
    """
    new_route = route[:i] + route[i : k + 1][::-1] + route[k + 1 :]
    return new_route


def simulated_annealing(initial_route, max_iter=20000, T0=100.0, alpha=0.9995):
    """
    退火算法

    Args:
        initial_route (_type_): 初始状态
        max_iter (int, optional): 迭代次数. Defaults to 20000.
        T0 (float, optional): 初始温度. Defaults to 100.0.
        alpha (float, optional): 退火系数. Defaults to 0.9995.
    """
    route = initial_route[:]
    best = route[:]
    best_len = path_length(best)
    current_len = best_len
    T = T0
    for _ in range(max_iter):
        # 随机选择两个位置进行 2-opt
        i = random.randint(0, N - 2)
        k = random.randint(i + 1, N - 1)
        new_route = two_opt_swap(route, i, k)

        new_len = path_length(new_route)
        delta = new_len - current_len

        # delta 为负，表示新路径更优了
        # delta 为正时，新解更差
        # T 是当前温度，温度越高，接受劣解的概率越大，有利于跳出局部最优
        if delta < 0 or random.random() < math.exp(-delta / T):
            route = new_route
            current_len = new_len
            if current_len < best_len:
                best = route[:]
                best_len = current_len

        T *= alpha  # 降温

        # 降到冰点结束
        if T < 1e-8:
            break

    return best, best_len


# ------------------------------------------------------
# 遗传算法实现（Ordered Crossover + swap mutation + tournament selection）
# ------------------------------------------------------
def create_population(pop_size):
    pop: list[list[int]] = []
    base = list(range(N))
    for _ in range(pop_size):
        indiv: list[int] = base[:]  # 个体基因
        random.shuffle(indiv)
        pop.append(indiv)
    return pop


def tournament_selection(
    pop: list[list[int]], fitnesses: list[float], k=3
) -> list[int]:
    """
    锦标赛选择（Tournament）兼顾以下：
        选择压力（selection pressure）：优秀个体更有机会被选中
        多样性（diversity）：仍然存在随机性，不会总是选最优解
    其它算法：轮盘赌选择（Roulette Wheel）、排名选择（Rank-based）
    """
    selected = random.sample(range(len(pop)), k)
    best = min(
        selected, key=lambda idx: fitnesses[idx]
    )  # 注意 fitness 用路径长度，越小越好
    return deepcopy(pop[best])


def ordered_crossover(a, b):
    """
    顺序交叉
    交叉决定“继承方式”，变异决定“探索能力”
    """
    start = random.randint(0, N - 2)
    end = random.randint(start + 1, N - 1)
    child = [-1] * N
    # 1. 拷贝子段
    child[start : end + 1] = a[start : end + 1]
    # 2. 按照 b 的顺序填充剩余位置
    b_idx = 0
    for i in range(N):
        if child[i] == -1:
            while b[b_idx] in child:
                b_idx += 1
            child[i] = b[b_idx]
    return child


def swap_mutation(indiv, mutation_rate=0.1):
    for i in range(N):
        if random.random() < mutation_rate:
            j = random.randint(0, N - 1)
            indiv[i], indiv[j] = indiv[j], indiv[i]


def genetic_algorithm(pop_size=100, generations=500, elite_size=2, mutation_rate=0.05):
    """
    遗传算法
        编码基因 -> 评估适应性 -> 保留精英(下一代的参照，不会更差) ->
        随机选择(提供遗传机会) -> 交叉(保留部分解) -> 变异(探索新解)
    Args:
        pop_size (int, optional): 种群规模. Defaults to 100.
        generations (int, optional): 演进代数. Defaults to 500.
        elite_size (int, optional): 保留精英数. Defaults to 2.
        mutation_rate (float, optional): 突变率. Defaults to 0.05.
    """

    best = None
    best_len = float("inf")

    pop = create_population(pop_size)
    for _ in range(generations):
        # 计算适应性
        fitnesses = [path_length(ind) for ind in pop]

        # 记录最优
        min_idx = min(range(len(pop)), key=lambda i: fitnesses[i])
        if fitnesses[min_idx] < best_len:
            best_len = fitnesses[min_idx]
            best = deepcopy(pop[min_idx])

        # 新一代
        new_pop: list[list[int]] = []
        # 精英保留
        sorted_idx = sorted(range(len(pop)), key=lambda i: fitnesses[i])
        for i in range(elite_size):
            new_pop.append(deepcopy(pop[sorted_idx[i]]))

        while len(new_pop) < pop_size:
            # 随机选择
            parent1 = tournament_selection(pop, fitnesses, k=3)
            parent2 = tournament_selection(pop, fitnesses, k=3)

            # 交叉
            child = ordered_crossover(parent1, parent2)

            # 变异
            swap_mutation(child, mutation_rate)
            new_pop.append(child)
        pop = new_pop
    return best, best_len


# ------------------------------------------------------
# 运行两种算法并测时，都属于元启发式算法（Metaheuristics）
# 优化方向：混合优化算法（Hybrid Algorithm）
# 用 GA 快速找到“较优解群体”，然后用 SA 对每个个体或最优个体进行局部优化
# ------------------------------------------------------
initial_route = list(range(N))
random.shuffle(initial_route)

# Simulated Annealing
start = time.time()
sa_route, sa_len = simulated_annealing(
    initial_route, max_iter=30000, T0=100.0, alpha=0.9996
)
sa_time = time.time() - start

# Genetic Algorithm
start = time.time()
ga_route, ga_len = genetic_algorithm(
    pop_size=120, generations=100, elite_size=4, mutation_rate=0.08
)
ga_time = time.time() - start

# 输出结果
print("城市数量:", N)
print("模拟退火 (SA) 最短环路长度: {:.4f}, 时间: {:.2f}s".format(sa_len, sa_time))
print("遗传算法 (GA) 最短环路长度: {:.4f}, 时间: {:.2f}s".format(ga_len, ga_time))


# 按路径顺序取得坐标，便于绘图
def coords_from_route(route):
    xs = [cities[i][1] for i in route] + [cities[route[0]][1]]
    ys = [cities[i][2] for i in route] + [cities[route[0]][2]]
    return xs, ys


sa_xs, sa_ys = coords_from_route(sa_route)
ga_xs, ga_ys = coords_from_route(ga_route)

# 绘图对比：两个子图
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(sa_xs, sa_ys, marker="o")
for i, idx in enumerate(sa_route):
    plt.text(cities[idx][1], cities[idx][2], str(idx))
plt.title("Simulated Annealing\nLength: {:.4f}".format(sa_len))

plt.subplot(1, 2, 2)
plt.plot(ga_xs, ga_ys, marker="o")
for i, idx in enumerate(ga_route):
    plt.text(cities[idx][1], cities[idx][2], str(idx))
plt.title("Genetic Algorithm\nLength: {:.4f}".format(ga_len))

plt.suptitle("TSP: SA vs GA ({} cities)".format(N))
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
