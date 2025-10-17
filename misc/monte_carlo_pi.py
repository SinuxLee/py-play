import numpy as np
import time


def monte_carlo_pi_batch(batch_size=10**6, num_batches=1000, seed=None):
    if seed is not None:
        np.random.seed(seed)

    pi_estimates = []

    for _ in range(num_batches):
        # 生成 batch_size 个点
        points = np.random.rand(batch_size, 2)
        # 距离平方，避免开根号
        distances_sq = points[:, 0] ** 2 + points[:, 1] ** 2
        points_inside = np.sum(distances_sq <= 1.0)
        # 估计 π
        pi_estimate = 4 * points_inside / batch_size
        pi_estimates.append(pi_estimate)

        print(time.time(), np.mean(np.array(pi_estimates)))

    pi_estimates = np.array(pi_estimates)
    # 平均值
    pi_mean = np.mean(pi_estimates)
    # 样本标准差
    pi_std = np.std(pi_estimates, ddof=1)
    # 标准误差
    se = pi_std / np.sqrt(num_batches)
    # 95%置信区间
    ci_lower = pi_mean - 1.96 * se
    ci_upper = pi_mean + 1.96 * se

    return pi_mean, se, (ci_lower, ci_upper), pi_estimates


start = time.time()
# 运行示例
pi_mean, se, ci, pi_estimates = monte_carlo_pi_batch(
    batch_size=10**8, num_batches=1000, seed=33
)
end = time.time()

# 蒙特卡洛求 π
print(f"估计 π 平均值: {pi_mean}")
print(f"标准误差: {se}")
print(f"95% 置信区间: {ci}")
print(f"耗时{end-start}")
