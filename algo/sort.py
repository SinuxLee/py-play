"""
实现难易程度：快速排序原地 > 堆排序 > 归并排序原地 > 希尔排序 > 插入排序 > 选择排序 > 冒泡排序
选择算法时需要考虑：
1. 数据规模 10^2 10^4 10^5 10^7
    小数据量：几十到几千个元素
    中等数据量：几万到几十万元素
    大数据量：百万到千万级甚至亿级元素
    亿级及以上考虑外部排序（External Sort），磁盘归并排序
2. 空间限制(考虑递归栈空间) O(1)
3. 时间复杂度 O(n) O(n^2) O(n log n)
4. 元素顺序稳定性
5. 方差 最好，最坏，平均情况
6. 评估，有序，逆序，局部有序(前中后)，完全乱序，重复数据占比
7. 特殊情况：数据为空，一个元素

工业/工程实践要求：
1. 高效
2. 稳定(同样数据得到固定结果)
3. 易实现(理解)
4. 适应性好(处理不同特征样本，时间/空间最好是相近的)
"""


# -------- 稳定的排序 --------
def bubble_sort(arr: list[int]) -> None:
    """
    冒泡排序
        每趟比较相邻的两个数
    Args:
        arr (list[int]): 待排序数据
    """
    length = len(arr)
    while length > 1:
        for i in range(length - 1):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
        length -= 1


def insert_sort(arr: list[int]) -> None:
    """
    插入排序
        默认第一个元素是有序的，从第二个开始依次插入到有序部分
        适合小规模数据(几十个) / 基本有序的数据
    Args:
        arr (list[int]): 待排序数据
    """
    length = len(arr)
    for i in range(1, length):
        v = arr[i]
        for j in range(i - 1, -1, -1):
            if arr[j] <= v:
                arr[j + 1] = v
                break

            arr[j + 1] = arr[j]
        else:
            arr[j] = v


# 鸡尾酒排序
# 桶排序
# 计数排序
# 归并排序
# 原地归并排
# 二叉排序树
# 鸽巢排序
# 基数排序
# 侏儒排序
# 图书馆排序
# 块排序


# Tim排序, V8、Java、 Python 中的实现
# 基于归并排序 + 插入排序
def insertion_sort(arr, left, right):
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def merge(arr, left, mid, right):
    left_part = arr[left : mid + 1]
    right_part = arr[mid + 1 : right + 1]

    i = j = 0
    k = left
    while i < len(left_part) and j < len(right_part):
        if left_part[i] <= right_part[j]:
            arr[k] = left_part[i]
            i += 1
        else:
            arr[k] = right_part[j]
            j += 1
        k += 1

    while i < len(left_part):
        arr[k] = left_part[i]
        i += 1
        k += 1

    while j < len(right_part):
        arr[k] = right_part[j]
        j += 1
        k += 1


# TimSort
def timsort(arr):
    size = 32
    n = len(arr)

    # 分段并用插入排序
    for start in range(0, n, size):
        end = min(start + size - 1, n - 1)
        insertion_sort(arr, start, end)

    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(n - 1, left + size - 1)
            right = min((left + 2 * size - 1), (n - 1))
            if mid < right:
                merge(arr, left, mid, right)
        size *= 2


# -------- 不稳定的排序 --------
def select_sort(arr: list[int]) -> None:
    """
    选择排序
        每趟选择一个较大的数与其它数比较
    Args:
        arr (list[int]): 待排序数据
    """
    pos = len(arr) - 1
    while pos > 0:
        idx = 0
        for i in range(1, pos + 1):
            if arr[idx] < arr[i]:
                idx = i

        if idx != pos:
            arr[idx], arr[pos] = arr[pos], arr[idx]
        pos -= 1


# 希尔排序，插入排序的改进版
def shell_sort(arr: list[int]) -> None:
    """
    希尔排序
        中等规模数据排序(几百~几千条)
        不同 gap 序列会影响性能：
            Shell 原始序列(n/2,n/4,...)
            Hibbard 序列((2^k - 1))
            Knuth 序列 (3^k - 1)/2
            Sedgewick 序列 max (9*4^j - 9*2^j + 1, 4^k - 3 * 2^k + 1)
    Args:
        arr (list[int]): 待排序数据
    """
    length = len(arr)
    gap = length // 2  # 初始间隔为数组长度的一半

    # 当 gap 缩小到 0 时结束
    while gap > 0:
        # 从 gap 开始遍历数组
        for i in range(gap, length):
            temp = arr[i]
            j = i
            # 对每个分组进行插入排序
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        # 缩小间隔
        gap //= 2


# 克洛弗排序
# 梳排序
# 平滑排序


def heapify(arr, n, i):
    largest = i  # 当前节点
    left = 2 * i + 1  # 左子节点
    right = 2 * i + 2  # 右子节点

    # 找到最大值
    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right

    # 如果最大值不是当前节点，交换并递归调整
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)


def heap_sort(arr: list[int]) -> None:
    """
    堆排序
        本质是利用部分有序集合的传递性完成比较，比如 a>b 且 b>c 则 a>c 从而减少比较/交换次数
        适合大数据量，百万~千万级
        没有额外空间开销
        时间复杂度非常稳定
    Args:
        arr (list[int]): 待排序数据
    """
    n = len(arr)

    # 构建最大堆
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    # 逐步交换堆顶到末尾，然后重新调整堆
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]  # 交换
        heapify(arr, i, 0)  # 调整堆


def quick_sort(arr: list[int], low: int, high: int) -> None:
    """
    快速排序
        用最左侧元素将 list 划分成两部分(分治策略)，将小于它的放左侧，否则放右侧
        时间复杂度方差较大
    Args:
        arr (list[int]): 待排序数据
    """
    if low >= high:
        return

    i, j = low, high
    guard = arr[low]

    while i < j:
        while arr[j] > guard and j > i:
            j -= 1

        while arr[i] <= guard and i < j:
            i += 1

        if i < j:
            arr[i], arr[j] = arr[j], arr[i]

    arr[low], arr[i] = arr[i], arr[low]

    quick_sort(arr, low, i - 1)
    quick_sort(arr, i + 1, high)


# 内省排序
# 一种结合了快速排序（Quick Sort）、堆排序（Heap Sort）和插入排序（Insertion Sort）的混合算法，C++ STL 的 std::sort 用的此算法

# 耐心排序

# PDQSort (Pattern-Defeating Quicksort)
# Rust、C++ Boost 中默认的 unstable 排序算法

if __name__ == "__main__":
    import random
    import copy

    data = [random.randint(1, 10) for _ in range(10)]
    print(data)
    copyed_data = copy.copy(data)
    copyed_data.sort()
    print(copyed_data)

    # bubble_sort(data)
    # select_sort(data)
    # insert_sort(data)
    # quick_sort(data, 0, len(data) - 1)
    # shell_sort(data)
    # heap_sort(data)
    timsort(data)
    print(data)
