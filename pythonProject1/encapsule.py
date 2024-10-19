class Person:
    def __init__(self):
        print("PP")
    def __display(self,n):
        self.n = n 
        print(self.n)
    def _display(self,n):
        self.n = n 
        print(self.n)
person = Person()
print(person)
# print(person.__display(2))
print(person._Person__display(3))
print(person._display(2))