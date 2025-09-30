import random

# 可以用来实现加权随机选择
def weighted_random(weights):
    total = sum(weights)
    r = random.randint(1, total)  # 在 1 ~ total 之间取随机数
    cumulative = 0
    for i, w in enumerate(weights):
        cumulative += w
        if r <= cumulative:
            return i

weights = [1, 3, 11, 9, 4]
results = [weights[weighted_random(weights)] for _ in range(20)]
print(results)

# 随机与掉落相关算法：
# 1. 加权随机 / 掉落表
# 就是你提到的这种权重随机。常用于装备掉落、抽卡、怪物刷新。

# 2.保底机制（Pity System）
# 比如抽卡 90 次必出五星，或者概率随抽取次数递增。
# 典型实现：每抽一次计数，超过阈值就直接发放或提高概率。

# 3. 无重复随机（洗牌算法 / Fisher–Yates shuffle）
# 适合卡牌洗牌、随机任务池，避免重复出现。

# 4. 伪随机修正
# 例如 Dota 里的暴击，不是完全独立的概率，而是“越久没触发，下次概率越高”，让玩家感觉更公平。

# ⚔ 战斗与数值：

# 5. 命中判定
# 命中 = 攻击者命中率 - 防御者闪避率，然后取随机数判定。
# 可以用线性、Sigmoid 等函数平滑概率。

# 6. 伤害波动
# 伤害 = 基础伤害 ± (一定百分比随机浮动)，让战斗更生动。

# 7. 经验/升级公式
# 常用等比、等差、指数型，甚至分段函数。比如：
# 经验值 = k * n^2 （n 为等级，k 控制难度曲线）

# 🗺 生成与玩法：

# 8. 程序化生成 (Procedural Generation)
# 地图、怪物属性、任务内容的随机生成。
# 常用噪声函数（Perlin Noise、Simplex Noise）。

# 9. 冷却缩减 / 衰减函数
# 技能冷却、buff 衰减、收益递减。通常用指数衰减或分段函数。

# 10. 匹配算法 (Matchmaking)
# 用 Elo、Glicko、MMR 等评分系统，给玩家匹配实力接近的对手。

# 玩家体验优化：

# 11. 掉落倾斜算法
# 玩家长时间没掉落稀有物品时，暗箱提升稀有掉落概率。
# （增强正反馈，避免挫败感）

# 12. 权重衰减随机
# 随机任务或副本避免重复，给最近出现过的条目降低权重。

# 13. 路径平滑 / 导航
# AI 走路、寻路时常用 A* + 平滑算法，避免看起来僵硬。
