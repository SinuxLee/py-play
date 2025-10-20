import random
import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# --- 参数设置 ---
N = 100              # 候选人总数
observation_ratio = 0.37  # 37% 规则
num_simulations = 10000   # 模拟次数

# --- 模拟函数 ---
def simulate_secretary_problem(N, observation_ratio):
    """
    使用 37% 规则模拟一次秘书问题
    返回选中候选人的能力值
    """
    # 生成 N 个候选人的随机能力值 (1 到 N)
    candidates = list(range(1, N + 1))
    random.shuffle(candidates)

    # 确定观察期长度
    observation_period = int(N * observation_ratio)
    
    # 在观察期内找到最高的能力值
    best_in_observation = max(candidates[:observation_period]) if observation_period > 0 else 0
    
    # 在选择期内寻找第一个比观察期最高分还高的人
    for i in range(observation_period, N):
        if candidates[i] > best_in_observation:
            return candidates[i]  # 找到并选择
            
    # 如果选择期内没找到，则选择最后一个
    return candidates[-1]

# --- 运行模拟 ---
selected_scores = []
optimal_selection_count = 0

for _ in range(num_simulations):
    score = simulate_secretary_problem(N, observation_ratio)
    selected_scores.append(score)
    if score == N:  # 如果选中了能力值最高的候选人
        optimal_selection_count += 1

# --- 结果分析 ---
average_score = np.mean(selected_scores)
optimal_selection_rate = optimal_selection_count / num_simulations

print(f"模拟参数: 候选人总数 N = {N}, 观察比例 = {observation_ratio:.2f}, 模拟次数 = {num_simulations}")
print("-" * 50)
print(f"选中候选人的平均能力值 (加权均值): {average_score:.2f}")
print(f"选中最佳候选人 (能力值={N}) 的频率: {optimal_selection_rate:.2%}")
