#### 一行代码实现求阶乘函数
```py
fac = lambda x: __import__('functools').reduce(int.__mul__, range(1, x + 1), 1)
```

#### 一行代码实现求最大公约数函数
```py
gcd = lambda x, y: y % x and gcd(y % x, x) or x
```

#### 一行代码实现判断素数的函数
```py
is_prime = lambda x: x > 1 and not [f for f in range(2, int(x ** 0.5) + 1) if x % f == 0]
```

#### 一行代码实现快速排序
```py
quick_sort = lambda items: len(items) and quick_sort([x for x in items[1:] if x < items[0]]) + [items[0]] + quick_sort([x for x in items[1:] if x > items[0]]) or items
```

#### 生成FizzBuzz列表
```py
['Fizz'[x % 3 * 4:] + 'Buzz'[x % 5 * 4:] or x for x in range(1, 101)]
```
