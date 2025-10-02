def f():
    pass

code = f.__code__
print(code.co_code) # bytecode
print(dir(code))
