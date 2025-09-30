# 用最小堆/最大堆代替排序，降低复杂度（O(n log k)）
# 优先队列（priority queue）
# 排序优化（堆排序，Top-K，实时中位数）
# 图论最短路/生成树（Dijkstra，Prim，A*）
# 调度/分配（会议室、任务调度、负载均衡）
# 数据流/滑动窗口/合并问题
# 编码/压缩（霍夫曼）

import heapq

# 可以用来优化Dijkstra算法，A*算法等

h: list[int] = [5, 7, 9, 11, 3]

heapq.heapify(h)
print(h)

heapq.heappush(h, 4)
print(h)

heapq.heappop(h)
print(h)

# Dijkstra 最短路
# Prim 最小生成树
# A* 启发式搜索
# Top-K 问题（如数据流中求前 K 大元素）
# 调度系统（根据优先级决定执行顺序）
# 事件驱动模拟（按时间顺序处理事件）
# 合并 K 个有序链表/数组
# A* 搜索：最小堆按 f = g + h（当前代价 + 启发式）排序取点。
# 最大堆选择负载最高的节点，最小堆选择负载最低的节点
# 两堆平衡 → O(log n) 插入，O(1) 查询中位数
# 霍夫曼编码：不断合并权值最小的两个节点 → 用最小堆
