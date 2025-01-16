from timeit import Timer
t = Timer("for i in range(1000):1+1")
print(t.timeit())