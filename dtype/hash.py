# 哈希表（Hash Table / Hash Map / Dictionary）
# 布隆过滤器（Bloom Filter）

d: dict[str, any] = {}
d["name"] = "zhangsan"
d["age"] = 20
d["coin"] = 100.5
d["is_vip"] = True
d["skills"] = ["python", "java", "c++"]
d["address"] = {"city": "beijing", "street": "chaoyang"}
d["greet"] = lambda: print("hello world")


print(d)

print(d.items())
print(d.keys())

s : set[str] = {"python", "java", "c++"}
s.add("go")
print(s)
