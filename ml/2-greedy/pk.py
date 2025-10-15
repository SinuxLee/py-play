import random

# 随机生成物品
n = 6  # 物品数量
W = 15  # 背包容量
# items = [(重量, 价值)]
items = [(random.randint(2, 10), random.randint(10, 60)) for _ in range(n)]

for i, (w, v) in enumerate(items):
    print(f"物品 {i+1}: 重量={w}, 价值={v}, 价值密度={v/w:.2f}")


# -------------------------------
#  贪心算法（分数背包）
# -------------------------------
def fractional_knapsack(items, W):
    total_value = 0
    capacity = W

    items_sorted = sorted(items, key=lambda x: x[1] / x[0], reverse=True)
    for w, v in items_sorted:
        if capacity >= w:
            total_value += v
            capacity -= w
        else:
            total_value += v * (capacity / w)  # 可分割
            break
    return total_value


# -------------------------------
#  动态规划（0-1 背包） 递推计算（状态转移）
# -------------------------------
def knapsack_01(items, W):
    n = len(items)

    # dp 记录递推信息
    # N 行表示，容量为 N 时，可放入的最大价值
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    for curr_cap in range(1, n + 1):
        w, v = items[curr_cap - 1]
        for curr_max_w in range(1, W + 1):
            if curr_max_w >= w:
                dp[curr_cap][curr_max_w] = max(dp[curr_cap - 1][curr_max_w], dp[curr_cap - 1][curr_max_w - w] + v)
            else:
                dp[curr_cap][curr_max_w] = dp[curr_cap - 1][curr_max_w]

    return dp[n][W]


# -------------------------------
# 比较
# -------------------------------
value_greedy = fractional_knapsack(items, W)
value_dp = knapsack_01(items, W)

print("\n💰 结果比较:")
print(f"分数背包（贪心算法）解: {value_greedy:.2f}")
print(f"0-1 背包（DP最优）解: {value_dp}")
