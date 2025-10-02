import inspect

def f():
    frame = inspect.currentframe(),
    print(frame)

f()