class Bank:
    def __init__(self,name,balance):
        self.name = name
        self.__balance = balance
        
    def get_balance(self):
        return self.__balance
b = Bank("Rahul","312312")
print(b.name)
print(b.get_balance())
print(b.__balance)
