# BFS 层次遍历（最短路径 / 最少步数）
# 双端队列 → 单调队列优化（滑动窗口 O(n) 解法）
# 循环队列（节省内存，流式处理）
# 优先队列 / 堆（最短路、调度、Top-K 优化）
# 多源/双向 BFS（指数级搜索降维为多项式）

from collections import deque
import queue

d: deque[int] = deque(i for i in range(10))
print(d)

d.append(99)
d.appendleft(999)
print(d)

d.pop()
d.popleft()
print(d)

print("-" * 20)
q: queue.SimpleQueue[int] = queue.SimpleQueue()
for i in range(10):
    q.put(i)

print(q.get())

# 任务调度：CPU 调度、操作系统进程队列
# 缓冲区：生产者-消费者模型，消息队列
# BFS（广度优先搜索）：遍历树/图时天然使用队列

# 滑动窗口最值（经典优化，LeetCode 239 Sliding Window Maximum）
# 回文判断：字符串前后比对

# 用于 固定长度缓存（环形缓冲区） 网络数据包、日志系统
# 可以避免数组扩容，节省空间和时间

# 双向 BFS：从起点和终点同时扩展，常见于最短路径问题（如单词接龙）。
# 多源 BFS：初始时将多个点入队，用来同时扩散（腐烂的橘子、火势蔓延）。
# 分层 BFS：图最短路时常用。

# 拓扑排序（Kahn 算法）：队列存入入度为 0 的节点，逐步消除边。
# 最大流算法（Edmonds-Karp）：使用 BFS + 队列寻找增广路径。
# 流量控制 / 滑动窗口限速：用队列保存最近一段时间的请求记录
