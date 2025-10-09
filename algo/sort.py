'''
    实现难易程度：快速排序原地 > 堆排序 > 归并排序原地 > 希尔排序 > 插入排序 > 选择排序 > 冒泡排序
'''
# -------- 稳定的排序 --------
def bubble_sort(arr: list[int]) -> None:
    """冒泡排序
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
    """插入排序
        默认第一个元素是有序的，从第二个开始依次插入到有序部分
        适合小规模数据 / 基本有序的数据
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
# Tim排序


# -------- 不稳定的排序 --------
def select_sort(arr: list[int]) -> None:
    """选择排序
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


# 希尔排序
# 克洛弗排序
# 梳排序
# 堆排序
# 平滑排序


def quick_sort(arr: list[int], low: int, high: int) -> None:
    """快速排序
        用最左侧元素将 list 划分成两部分(分治策略)，将小于它的放左侧，否则放右侧
    Args:
        arr (list[int]): _description_
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
    quick_sort(data, 0, len(data) - 1)
    print(data)
