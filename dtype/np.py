import numpy as np

matrix = np.random.randint(0, 100, size=(5, 5))
print("原矩阵:\n", matrix)

# 最大值和最小值
max_val = np.max(matrix)
min_val = np.min(matrix)
max_pos = np.unravel_index(np.argmax(matrix), matrix.shape)
min_pos = np.unravel_index(np.argmin(matrix), matrix.shape)
print("最大值:", max_val, "位置:", max_pos)
print("最小值:", min_val, "位置:", min_pos)

# 大于平均值置1，否则置0
mean_val = np.mean(matrix)
binary_matrix = (matrix > mean_val).astype(int)
print("二值矩阵:\n", binary_matrix)


# ==================================================
# 生成10名学生的5门课成绩（0~100）
scores = np.random.randint(0, 101, size=(10, 5))
print("成绩矩阵:\n", scores)

# 每个学生平均成绩
avg_scores = np.mean(scores, axis=1)
print("每个学生平均成绩:\n", avg_scores)

# 每门课程平均成绩
course_avg = np.mean(scores, axis=0)
print("每门课程平均成绩:\n", course_avg)

# 找出所有及格（>=60）的成绩
pass_mask = scores >= 60
print("及格情况:\n", pass_mask)

# 将未及格的成绩标记为0
scores_adjusted = np.where(scores >= 60, scores, 0)
print("调整后的成绩:\n", scores_adjusted)


# ==================================================
# 模拟一个 8x8 的灰度图像，像素值 0~255
image = np.random.randint(0, 256, size=(8, 8))
print("原图像:\n", image)

# 找到最大亮度和最小亮度像素位置
max_pixel = np.unravel_index(np.argmax(image), image.shape)
min_pixel = np.unravel_index(np.argmin(image), image.shape)
print("最亮像素位置:", max_pixel)
print("最暗像素位置:", min_pixel)

# 将像素值大于128的设为255，其余设为0（二值化）
binary_image = np.where(image > 128, 255, 0)
print("二值化图像:\n", binary_image)


# ==================================================
# 模拟5支股票过去7天的价格
prices = np.random.randint(100, 200, size=(7, 5))
print("股票价格:\n", prices)

# 计算每日收益率 (百分比变化)
returns = (prices[1:] - prices[:-1]) / prices[:-1] * 100
print("每日收益率(%):\n", returns)

# 计算每支股票的平均收益率
avg_returns = np.mean(returns, axis=0)
print("平均收益率(%):\n", avg_returns)

# 找出收益率为正的天数
positive_days = returns > 0
print("收益为正的天数:\n", positive_days)

# ==================================================
# 模拟带缺失值的数据
data = np.random.randint(0, 100, size=(5, 5)).astype(float)
data[1, 2] = np.nan
data[3, 0] = np.nan
print("原始数据:\n", data)

# 找到 NaN 位置
nan_mask = np.isnan(data)
print("NaN位置:\n", nan_mask)

# 将 NaN 替换为列平均值
col_mean = np.nanmean(data, axis=0)
indices = np.where(np.isnan(data))
data[indices] = np.take(col_mean, indices[1])
print("填充后的数据:\n", data)

# ==================================================
# 模拟10名学生总成绩
total_scores = np.random.randint(0, 101, size=10)
print("总成绩:", total_scores)

# 学生成绩排名
rank_indices = np.argsort(-total_scores)  # 降序
print("排名索引:", rank_indices)

# 根据排名输出成绩
sorted_scores = total_scores[rank_indices]
print("降序排序后的成绩:", sorted_scores)

# 前3名成绩
top3_scores = sorted_scores[:3]
print("前三名成绩:", top3_scores)

# ==================================================
# 模拟10个弹簧振子的位移随时间变化
# 假设位移公式：x(t) = A * sin(w * t + phi)
num_springs = 10
num_timepoints = 50
A = np.random.uniform(1, 5, size=num_springs)      # 振幅
w = np.random.uniform(0.5, 2, size=num_springs)    # 角频率
phi = np.random.uniform(0, np.pi, size=num_springs) # 初相位

t = np.linspace(0, 10, num_timepoints)  # 时间点
# 使用广播计算每个弹簧在每个时间点的位移
x = A[:, np.newaxis] * np.sin(w[:, np.newaxis] * t + phi[:, np.newaxis])

print("弹簧位移矩阵 shape:", x.shape)
print(x)

# ==================================================
# 模拟30天的温度数据，单位：℃，10个城市
temps = np.random.randint(-5, 35, size=(30, 10))
print("温度矩阵:\n", temps)

# 每天的最高温度和最低温度
daily_max = np.max(temps, axis=1)
daily_min = np.min(temps, axis=1)
print("每天最高温度:", daily_max)
print("每天最低温度:", daily_min)

# 找出温度高于30℃的天数
hot_days_mask = temps > 30
hot_days_count = np.sum(hot_days_mask, axis=0)  # 每个城市
print("每个城市高温天数:", hot_days_count)

# 计算每个城市的平均温度
city_avg_temp = np.mean(temps, axis=0)
print("每个城市平均温度:", city_avg_temp)

# ==================================================
# 使用蒙特卡洛方法估算 π
num_points = 10**7
x = np.random.rand(num_points)
y = np.random.rand(num_points)

# 在单位圆内的点
inside_circle = x**2 + y**2 <= 1
pi_estimate = 4 * np.sum(inside_circle) / num_points
print("估算的 π 值:", pi_estimate)

# 模拟 5x5 图像
image = np.random.randint(0, 256, size=(5, 5))
print("原图像:\n", image)

# ==================================================
# 定义简单均值滤波器 3x3
kernel = np.ones((3, 3)) / 9

# 对图像进行卷积（忽略边界，中心3x3区域）
convolved = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        region = image[i:i+3, j:j+3]
        convolved[i, j] = np.sum(region * kernel)

print("卷积后的图像:\n", convolved)


# ==================================================
# 模拟用户对商品评分矩阵 (5用户 x 6商品)
ratings = np.random.randint(1, 6, size=(5, 6)).astype(float)
ratings[0, 2] = np.nan
ratings[3, 5] = np.nan
print("原评分矩阵:\n", ratings)

# 填充缺失值为每个商品的平均评分
col_mean = np.nanmean(ratings, axis=0)
indices = np.where(np.isnan(ratings))
ratings[indices] = np.take(col_mean, indices[1])
print("填充后的评分矩阵:\n", ratings)

# 计算每个用户的平均评分
user_avg = np.mean(ratings, axis=1)
print("每个用户平均评分:", user_avg)


# ==================================================
# 1. 模拟数据：10个用户对8部电影评分，评分1~5，部分缺失
ratings = np.random.randint(1, 6, size=(10, 8)).astype(float)
ratings[1, 3] = np.nan
ratings[4, 6] = np.nan
ratings[7, 0] = np.nan
print("原评分矩阵:\n", ratings)

# 2. 处理缺失值：用每部电影的平均分填充
col_mean = np.nanmean(ratings, axis=0)
indices = np.where(np.isnan(ratings))
ratings[indices] = np.take(col_mean, indices[1])
print("填充后的评分矩阵:\n", ratings)

# 3. 每个用户平均评分
user_avg = np.mean(ratings, axis=1)
print("每个用户平均评分:", user_avg)

# 4. 每部电影平均评分
movie_avg = np.mean(ratings, axis=0)
print("每部电影平均评分:", movie_avg)

# 5. 找出评分高于用户平均分的评分
high_scores_mask = ratings > user_avg[:, np.newaxis]
print("评分高于用户平均的矩阵:\n", high_scores_mask)

# 6. 为每个用户推荐评分最高的电影（假设未看过电影的评分为平均分）
recommendation_index = np.argmax(ratings, axis=1)
print("每个用户推荐电影索引:", recommendation_index)
