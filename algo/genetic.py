# Python genetic algorithm demo for teaching
# This cell runs a full demo: binary-encoded GA optimizing a 1D continuous function.
# It will print progress and show two plots:
# 1) The objective function and the final population positions
# 2) Convergence (best / mean fitness per generation)
# The code is annotated in Chinese for teaching purposes.

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
import platform

# 解决显示汉字的问题
system = platform.system()
if system == "Windows":
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
elif system == "Darwin":  # macOS
    plt.rcParams["font.sans-serif"] = ["PingFang SC"]
else:  # Linux
    plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei"]

plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示为方块的问题

np.random.seed(42)  # 固定随机性以便复现


# --- 问题定义 ---
# 我们要优化的目标函数（示例）：在区间 [-1, 2] 上寻找 x 使得 f(x) 最大
def f(x):
    # 这是个有多个局部最优的测试函数，适合教学演示
    return x * np.sin(10 * np.pi * x) + 2.0 * (x - 0.5) ** 2


X_MIN, X_MAX = -1.0, 2.0  # 搜索空间


# --- 二进制编码/解码 ---
def decode_individual(bits, n_bits=20, x_min=X_MIN, x_max=X_MAX):
    """把二进制数组解码为区间 [x_min, x_max] 上的实数 x"""
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    max_int = 2**n_bits - 1
    x = x_min + (x_max - x_min) * value / max_int
    return x


def encode_value(x, n_bits=20, x_min=X_MIN, x_max=X_MAX):
    """把实数 x 编码为二进制列表"""
    max_int = 2**n_bits - 1
    ratio = (x - x_min) / (x_max - x_min)
    integer = int(round(ratio * max_int))
    # 防止越界
    integer = max(0, min(max_int, integer))
    bits = [(integer >> i) & 1 for i in range(n_bits - 1, -1, -1)]
    return np.array(bits, dtype=int)


# --- GA 操作 ---
def init_population(pop_size, n_bits):
    return np.random.randint(0, 2, size=(pop_size, n_bits))


def fitness_population(pop, n_bits):
    xs = np.array([decode_individual(ind, n_bits) for ind in pop])
    fits = f(xs)
    return fits, xs


def tournament_selection(pop, fits, k=3):
    """锦标赛选择，返回选中的个体索引"""
    pop_size = len(pop)
    winners = []
    for _ in range(pop_size):
        aspirants = np.random.randint(0, pop_size, size=k)
        winner = aspirants[np.argmax(fits[aspirants])]
        winners.append(winner)
    return np.array(winners, dtype=int)


def single_point_crossover(parent1, parent2, crossover_rate=0.9):
    n = len(parent1)
    if np.random.rand() < crossover_rate:
        point = np.random.randint(1, n)  # 交叉点（不在端点）
        child1 = np.concatenate([parent1[:point], parent2[point:]])
        child2 = np.concatenate([parent2[:point], parent1[point:]])
    else:
        child1 = parent1.copy()
        child2 = parent2.copy()
    return child1, child2


def bit_flip_mutation(individual, mutation_rate=0.01):
    mask = np.random.rand(len(individual)) < mutation_rate
    individual[mask] = 1 - individual[mask]
    return individual


# --- GA 主循环 ---
@dataclass
class GAParams:
    pop_size: int = 50  # 种群大小
    n_bits: int = 20  # 染色体长度
    n_generations: int = 100  # 模拟遗传多少代
    crossover_rate: float = 0.9  # 交叉率
    mutation_rate: float = 0.01  # 变异率
    elitism: int = 1  # 保留的精英数量


def run_ga(params: GAParams, verbose=True):
    pop = init_population(params.pop_size, params.n_bits)
    best_history = []
    mean_history = []
    best_x_history = []

    for gen in range(params.n_generations):
        fits, xs = fitness_population(pop, params.n_bits)
        # 记录数据
        best_idx = np.argmax(fits)
        best_fit = fits[best_idx]
        mean_fit = np.mean(fits)
        best_x = xs[best_idx]
        best_history.append(best_fit)
        mean_history.append(mean_fit)
        best_x_history.append(best_x)

        if verbose and (gen % 10 == 0 or gen == params.n_generations - 1):
            print(
                f"Generation {gen:3d} | Best fitness: {best_fit:.6f} | x = {best_x:.6f} | Mean fitness: {mean_fit:.6f}"
            )

        # 选择
        selected_idx = tournament_selection(pop, fits, k=3)
        mating_pool = pop[selected_idx]

        # 生成下一代
        next_pop = []
        # 精英保留：把当前最好的个体复制到下一代
        elites_idx = np.argsort(fits)[-params.elitism :]
        elites = pop[elites_idx].copy()

        # 交叉和变异（以配对方式）
        for i in range(0, params.pop_size - params.elitism, 2):
            p1 = mating_pool[i % len(mating_pool)]
            p2 = mating_pool[(i + 1) % len(mating_pool)]
            c1, c2 = single_point_crossover(p1, p2, params.crossover_rate)  # 交叉
            c1 = bit_flip_mutation(c1, params.mutation_rate)  # 变异
            c2 = bit_flip_mutation(c2, params.mutation_rate)
            next_pop.append(c1)
            if len(next_pop) < params.pop_size - params.elitism:
                next_pop.append(c2)

        next_pop = np.array(next_pop)
        # 将精英插回下一代
        if params.elitism > 0:
            next_pop = np.vstack([next_pop, elites])
        pop = next_pop

    # 结束后返回结果和历史数据
    final_fits, final_xs = fitness_population(pop, params.n_bits)
    best_final_idx = np.argmax(final_fits)
    result = {
        "best_fitness": final_fits[best_final_idx],
        "best_x": final_xs[best_final_idx],
        "population": pop,
        "fitness": final_fits,
        "x_values": final_xs,
        "best_history": np.array(best_history),
        "mean_history": np.array(mean_history),
        "best_x_history": np.array(best_x_history),
    }
    return result


# 运行 demo
params = GAParams(
    pop_size=600,
    n_bits=24,
    n_generations=200,
    crossover_rate=0.9,
    mutation_rate=0.01,
    elitism=5,
)
res = run_ga(params, verbose=True)

# 打印最终结果
print("\n=== 最终结果 ===")
print(f"Best fitness = {res['best_fitness']:.6f}  at x = {res['best_x']:.6f}")

# 画图：目标函数与最终种群位置
xs_plot = np.linspace(X_MIN, X_MAX, 1000)
ys_plot = f(xs_plot)

plt.figure(figsize=(10, 4))
plt.plot(xs_plot, ys_plot)

# 在曲线上标出最终个体位置（用小圆点）
final_xs = res["x_values"]
final_ys = res["fitness"]
plt.scatter(final_xs, final_ys)
plt.title("目标函数与最终种群位置 (每个点代表一个个体)")
plt.xlabel("x")
plt.ylabel("f(x)")
plt.grid(True)
plt.show(block=False)

# 画图：收敛曲线
plt.figure(figsize=(10, 4))
gens = np.arange(len(res["best_history"]))
plt.plot(gens, res["best_history"], label="best")
plt.plot(gens, res["mean_history"], label="mean")
plt.title("收敛曲线：最优和平均适应度随代数变化")
plt.xlabel("Generation")
plt.ylabel("Fitness")
plt.legend()
plt.grid(True)
plt.show()

# 简要总结（打印）
print("\n小结：")
print(" - 使用二进制编码和单点交叉、位翻转变异的经典 GA 示例。")
print(" - 通过精英保留 (elitism) 避免最优解丢失。")
print(" - 观察收敛曲线可以了解算法是否陷入局部最优或仍在改进。")
print(
    " - 可修改参数：种群大小 (pop_size)、染色体长度 (n_bits)、变异率 (mutation_rate)、交叉率 (crossover_rate)、精英数量 (elitism) 来观察不同效果。"
)

'''
创意编程：
OpenProcessing
这是一个专注于创意编码的社区，支持 p5.js 和 Processing。你可以浏览他人作品、获取灵感，甚至直接修改代码进行实验。
👉 访问：https://openprocessing.org/

Creative Coding Club
由 Nat Cooper 创建，旨在提供创意编码挑战，帮助开发者和艺术家提升技能。
👉 访问：https://creativecoding.club

Codewars
提供社区创建的编程挑战（称为 kata），涵盖多种编程语言，适合提升编码技巧。
👉 访问：https://www.codewars.com/

CodinGame
通过游戏化的编程挑战，让你在解决问题的同时提升编程能力。
👉 访问：https://www.codingame.com/start/

Advent of Code
每年12月举办的编程挑战，提供有趣的编程题目，适合节日期间练习。
👉 访问：https://adventofcode.com/

Hour of Code
由 Code.org 提供，适合初学者的编程入门教程，内容丰富，易于上手。
👉 访问：https://hourofcode.com/us/learn
'''

# https://thecodingtrain.com/challenges
# https://editor.p5js.org/codingtrain/sketches/wb-QHVXBq
# https://github.com/sahil-tah/Flappy-Learn
# https://github.com/nishantkr18/FlappyBirdOnJavascript/tree/gh-pages
# https://thecodingtrain.com/challenges/100-neuroevolution-flappy-bird#part-5
# 自动玩小游戏，生成关卡且自动完成

# 播主：
# Daniel Shiffman / The Coding Train
# Coding Math / Daniel Shiffman
# Andreas Refsgaard / Creative Coding Shorts

