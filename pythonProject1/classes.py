class A:
    def method(self):
        print("A.method() called")


class B:
    def method(self):
        print("B.method() called")


class C(A, B):
    pass


class D(B, C):
    pass


d = D()
d.method()

# class A(object):
#     def display(self):
#         print(f" From class A")
# class B(A):
#     def display(self):
#         print(f" From class B")
# class C(A):
#     def display(self):
#         print(f" From class C")
# class E(C, B):
#     def display(self):
#         print(f" From class E")
# E().display()
# print(C.mro())

# class MyClass:
#     @staticmethod
#     def foo():
#         print( "hi")
#
#     @staticmethod
#     def bar():
#         MyClass.foo()
#
# my = MyClass.foo()
#
# class MyClass:
#     @classmethod
#     def foo(cls):
#         print ("hi")
#
#     @classmethod
#     def bar(cls):
#         cls.foo()
#
# my1 = MyClass.foo()

# This way, at least you don't have to repeat the name of the class.
