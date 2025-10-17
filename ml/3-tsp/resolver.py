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
N = 40
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
    return route[:i] + route[i : k + 1][::-1] + route[k + 1 :]


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
# 蚁群算法（Ant Colony Optimization, ACO）
# ------------------------------------------------------
def ant_colony_optimization(
    num_ants=40, generations=200, alpha=1.0, beta=5.0, rho=0.5, Q=100
):
    # 初始化信息素矩阵
    pheromone = [[1.0 for _ in range(N)] for _ in range(N)]
    best_route, best_len = None, float("inf")

    for _ in range(generations):
        all_routes = []
        all_lengths = []

        for idx in range(num_ants):
            unvisited = list(range(N))
            route = [idx % N]  # 每只蚂蚁起点不同
            unvisited.remove(route[0])
            # route = [unvisited.pop(random.randint(0, len(unvisited) - 1))] # 随机起点

            # 模拟走完所有城市
            while unvisited:
                i = route[-1]  # 上一城市
                probs = []
                for j in unvisited:
                    tau = pheromone[i][j] ** alpha
                    eta = (1.0 / dist[i][j]) ** beta
                    probs.append(tau * eta)
                total = sum(probs)
                probs = [p / total for p in probs]

                # 轮盘赌选择
                r = random.random()
                cum = 0
                for idx, p in enumerate(probs):
                    cum += p
                    if r <= cum:
                        next_city = unvisited.pop(idx)
                        break
                route.append(next_city)

            L = path_length(route)
            all_routes.append(route)
            all_lengths.append(L)
            if L < best_len:
                best_route, best_len = route[:], L

        # 信息素挥发与更新
        for i in range(N):
            for j in range(N):
                pheromone[i][j] *= 1 - rho

        for route, L in zip(all_routes, all_lengths):
            for i in range(N):
                a, b = route[i], route[(i + 1) % N]
                pheromone[a][b] += Q / L
                pheromone[b][a] += Q / L

    return best_route, best_len


# ------------------------------------------------------
# 混合算法
# ------------------------------------------------------
def aco_with_sa_local_search(
    num_ants=40,  # 蚂蚁数量
    generations=200,  # 模拟多少代
    alpha=1.0,  # 对信息素的依赖度，为 0 表示随机选择
    beta=5.0,  # 对启发函数的依赖度，为 0 则不考虑成本(距离)
    rho=0.5,  # 信息素挥发系数, 越大挥发越快
    Q=100,  # 信息素常数
    sa_prob=0.3,  # 启用退火优化概率
    sa_iter=500,  # 退火迭代次数
):
    """
    混合算法：蚁群算法 + 模拟退火局部优化
    sa_prob: 每代对部分最优蚂蚁使用局部优化的概率
    """
    pheromone = [
        [1.0 for _ in range(N)] for _ in range(N)
    ]  # 信息素，蚂蚁跟踪路径的依据
    best_route, best_len = None, float("inf")

    for _ in range(generations):
        all_routes, all_lengths = [], []

        for _ in range(num_ants):
            unvisited = list(range(N))
            route = [unvisited.pop(random.randint(0, N - 1))]

            while unvisited:
                i = route[-1]
                probs = []

                # 计算下一站的概率
                for j in unvisited:
                    tau = pheromone[i][j] ** alpha  # 查看信息素
                    eta = (1.0 / dist[i][j]) ** beta  # 距离越远此数越小
                    probs.append(tau * eta)
                total = sum(probs)
                probs = [p / total for p in probs]

                # 轮盘赌选择, 按权重随机选
                r, cum = random.random(), 0
                for idx, p in enumerate(probs):
                    cum += p
                    if r <= cum:
                        next_city = unvisited.pop(idx)
                        break
                route.append(next_city)

            L = path_length(route)

            # 对部分优质个体进行局部优化（模拟退火）
            if random.random() < sa_prob:
                route_sa, L_sa = simulated_annealing(
                    route, max_iter=sa_iter, T0=50.0, alpha=0.995
                )
                if L_sa < L:
                    route, L = route_sa, L_sa

            all_routes.append(route)
            all_lengths.append(L)
            if L < best_len:
                best_len, best_route = L, route[:]

        # 信息素衰减
        for i in range(N):
            for j in range(N):
                pheromone[i][j] *= 1 - rho

        # 在刚走过的路上添加信息素
        for route, L in zip(all_routes, all_lengths):
            for i in range(N):
                a, b = route[i], route[(i + 1) % N]
                pheromone[a][b] += Q / L
                pheromone[b][a] += Q / L

    return best_route, best_len


# ======================================================
# 运行三种算法并比较
# ======================================================
initial_route = list(range(N))
random.shuffle(initial_route)

# Simulated Annealing
start = time.time()
sa_route, sa_len = simulated_annealing(
    initial_route, max_iter=40000, T0=100.0, alpha=0.9998
)
sa_time = time.time() - start

# Genetic Algorithm
start = time.time()
ga_route, ga_len = genetic_algorithm(
    pop_size=120, generations=200, elite_size=4, mutation_rate=0.08
)
ga_time = time.time() - start

start = time.time()
aco_route, aco_len = ant_colony_optimization(num_ants=100, generations=200)
aco_time = time.time() - start

# mixed algo
start = time.time()
aco_sa_route, aco_sa_len = aco_with_sa_local_search(num_ants=40, generations=200)
aco_sa_time = time.time() - start


print("城市数量:", N)
print(f"模拟退火 (SA): {sa_len:.4f}, 用时 {sa_time:.2f}s")
print(f"遗传算法 (GA): {ga_len:.4f}, 用时 {ga_time:.2f}s")
print(f"蚁群算法 (ACO): {aco_len:.4f}, 用时 {aco_time:.2f}s")
print(f"混合算法 (ACO+SA): {aco_sa_len:.4f}, 用时 {aco_sa_time:.2f}s")


# ------------------------------------------------------
# 运行三种算法并测时，都属于元启发式算法（Metaheuristics）
# 优化方向：混合优化算法（Hybrid Algorithm）
# 用 GA 快速找到“较优解群体”，然后用 SA 对每个个体或最优个体进行局部优化
# ------------------------------------------------------
def coords_from_route(route):
    xs = [cities[i][1] for i in route] + [cities[route[0]][1]]
    ys = [cities[i][2] for i in route] + [cities[route[0]][2]]
    return xs, ys


show_ui = False
if show_ui:
    plt.figure(figsize=(16, 5))

    for i, (route, name, L) in enumerate(
        [
            (sa_route, "Simulated Annealing", sa_len),
            (ga_route, "Genetic Algorithm", ga_len),
            (aco_route, "Ant Colony Optimization", aco_len),
            (aco_sa_route, "Aco With SA Local Search", aco_sa_len),
        ]
    ):
        xs, ys = coords_from_route(route)
        plt.subplot(1, 4, i + 1)
        plt.plot(xs, ys, marker="o")
        for j, idx in enumerate(route):
            plt.text(cities[idx][1], cities[idx][2], str(idx))
        plt.title(f"{name}\nLength: {L:.2f}")

    plt.suptitle(f"TSP Comparison: SA vs GA vs ACO vs Mixed ({N} cities)")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()
