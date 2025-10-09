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
    for i in range(1, 20):
        for j in range(1, i + 1):
            print(f"{j}*{i}={i*j}", end=" ")
        print()


def foo(*args, **kwargs):
    print(args)
    print(kwargs)


def strStr(haystack: str, needle: str) -> int:
    need_len = len(needle)
    need_idx = 0

    hay_len = len(haystack)
    hay_idx = 0

    while hay_len - hay_idx > need_len - need_idx:
        if haystack[hay_idx+need_idx] != needle[need_idx]:
            hay_idx += 1
            need_idx = 0
            continue
        
        need_idx += 1
        if need_idx >= need_len:
            return hay_idx

    return -1


def main():
    # foo(3, 2.1, True, name='libz', age=43, gpa=4.95)
    print(strStr("sadbutsad", "sad"))
    print(strStr("mississippi", "issip"))


if __name__ == "__main__":
    main()
