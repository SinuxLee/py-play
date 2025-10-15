import numpy as np
from numpy.typing import NDArray


def standardize(data: NDArray[np.float64]) -> NDArray[np.float64]:
    """
    对输入数据进行标准化处理。
    经过标准化后的数据，均值为 0 ，标准差为 1

    参数:
        data (NDArray[np.float64]): 输入的一维或二维浮点数组。

    返回:
        NDArray[np.float64]: 标准化后的数组。
    """
    mean: float = float(np.mean(data))
    std: float = float(np.std(data))
    standardized_data: NDArray[np.float64] = (data - mean) / std
    return standardized_data


if __name__ == "__main__":
    arr: NDArray[np.float64] = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    result: NDArray[np.float64] = standardize(arr)
    print("原始数据:", arr)
    print("标准化结果:", result)

    print("=" * 8, "数组创建与初始化", "=" * 8)
    a = np.array([1, 2, 3])
    z = np.zeros((2, 3))
    print("zeros:\n", z)

    o = np.ones((2, 3))
    print("ones:\n", o)

    I = np.eye(3)  # 单位矩阵
    print("eye:\n", I)

    r = np.arange(0, 10, 3)  # 10 个 等间隔为 3 的数列
    print("arange:\n", r)

    l = np.linspace(0, 1, 5)  # 5 个等间距数
    print("linspace:\n", l)

    x = np.random.rand(3, 3)  # [0,1) 随机数
    print("rand:\n", x)

    y = np.random.randn(3, 3)  # 标准正态分布随机数
    print("randn:\n", y)
