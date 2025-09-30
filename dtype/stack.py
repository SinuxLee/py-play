# 递归 → 迭代（节省空间 / 避免栈溢出）
# 单调栈（O(n²) → O(n)）
# 辅助栈（O(n) 维护 → O(1) 查询最值）
# 表达式与括号匹配（简化解析逻辑）
# 图/树遍历（更安全更可控）

import queue

# list 本质是动态数组
l: list[int] = [i for i in range(10)]

l.append(99)
l.insert(0, 999)

print(l)
while l:
    print(l.pop(), end=" ")
print()

print("-" * 20)
lifo: queue.LifoQueue[int] = queue.LifoQueue()

lifo.put(1)
lifo.put(2)
lifo.put(3)

print(lifo.get())
print(lifo.get())

# 回溯算法：显式使用栈来替代递归，比如 DFS（深度优先搜索）

# 单调栈（Monotonic Stack），最小栈 / 最大栈（LeetCode 155. Min Stack）

# 括号匹配（Valid Parentheses, LeetCode 20）
# 逆波兰表达式求值（Evaluate Reverse Polish Notation, LeetCode 150）
# 中缀转后缀表达式（Shunting Yard 算法）

# 二叉树迭代遍历：前序/中序/后序都可以用栈模拟

# Tarjan 算法（强连通分量，基于 DFS + 栈）

# 区间合并问题中用栈存放候选区间
