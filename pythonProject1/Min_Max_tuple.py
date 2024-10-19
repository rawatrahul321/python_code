arr =  [1,2,5,6,4,33]
largest = arr[0]
second_largest = arr[0]
for i in range(1,len(arr)):
    if arr[i]>largest:
        second_largest = largest
        largest = arr[i]
    elif arr[i]>second_largest:
        second_largest = arr[i]
print(second_largest)



# def Findel(tup,K):
#     result = []
#     temp = sorted(tup)
#     print(temp)
#     for i, val in enumerate(temp):
#         print(i,val)
#         if i < K or i >= len(temp) - K:
#             result.append(val)
#     result = tuple(result)
#     # printing result
#     print("Max and Min K elements : ",result)
#
# tup = (13, 10, 23, 2, 5, 6, 12)
# K = 1
# print("The original tuple: ", tup)
# Findel(tup,K)
