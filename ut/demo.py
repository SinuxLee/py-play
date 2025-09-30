#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import random
import time

random.seed(time.time())


def add(a: int, b: int) -> int:
    return a + b


def read_csv(file_path: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)  # 能处理带引号、转义符、空格的复杂 CSV
        rows = list(reader)
        headers = rows[1]

    return [dict(zip(headers, row)) for row in rows[5:]]


def print_table_9x9():
    for i in range(1, 10):
        for j in range(1, i + 1):
            print(f"{j}*{i}={i*j}\t", end="")
        print()


# 比较相邻的两个数
def bubble_sort(arr: list[int]) -> None:
    length = len(arr)
    while length > 1:
        for i in range(length - 1):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
        length -= 1


# 其中一个较大的数与其它数比较
def select_sort(arr: list[int]) -> None:
    length = len(arr)
    while length > 1:
        idx = 0
        for i in range(length):
            if arr[idx] < arr[i]:
                idx = i
        arr[idx], arr[length - 1] = arr[length - 1], arr[idx]
        length -= 1
        print(arr)
    

def main():
    arr = [random.randint(1, 100) for _ in range(10)]
    arr = [1, 64, 1, 41, 96, 35, 56, 100, 97, 23]
    print("Original array:", arr)
    select_sort(arr)
    print("Sorted array:", arr)


if __name__ == "__main__":
    main()
