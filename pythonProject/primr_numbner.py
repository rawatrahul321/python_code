lower = 900
upper = 1000

for num in range(lower, upper + 1):
   # all prime numbers are greater than 1
   if num > 1:
       for i in range(2, num):
           if (num % i) == 0:
               break
       else:
           print(num,end= " ")

# Memory Save Fibonacci Series:-

n = int(input("Enter tHe number:"))
p2 = 0
p1 = 1
for i in range(2, n + 1):
    cur = p2 + p1
    p2 = p1
    p1 = cur
    print(p1, end=" ")
