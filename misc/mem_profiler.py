# pip install memory_profiler
# python3 -m memory_profiler mem_profiler.py

@profile
def eat_memory():
    items = []
    for _ in range(1000000):
        items.append(object())
    return items


eat_memory()
