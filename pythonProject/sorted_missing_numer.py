listA = [1,5,6, 7,11,14]
# listA = [7,8,9,11,12]
res = []
print(listA,listA[1:])
for m,n in zip(listA,listA[1:]):
   if n - m > 1:
      for i in range(m+1,n):
         res.append(i)
print("Missing elements from the list : \n" ,res)

# Implement a method to perform basic string compression using the counts of repeated characters. For example, the string "aabcccccaaa" would become "a2b1c5a3".
