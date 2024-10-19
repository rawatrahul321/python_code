class Foo:
  def printLine(self):
    print('Print Something')

print(callable(Foo))

InstanceOfFoo = Foo
# Raises an Error
# 'Foo' object is not callable
InstanceOfFoo.printLine(2)

# def sum_digits(a,b):
#     while b!=0:
#         a+=1
#         b-=1
#     return  a
# print(sum_digits(22+11,22))