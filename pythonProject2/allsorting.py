def bubble_sort(n):
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(n)-1):
            if n[i]>n[i+1]:
                n[i],n[i+1]=n[i+1],n[i]
                swapped = True
    return n
print(bubble_sort([3,7,9,2,1]))

# li = [23,2,33,44,3,22]
# for i in range(len(li)):
#     for j in range(i+1,len(li)):
#         if li[i]>li[j]:
#             li[i],li[j]=li[j],li[i]
# for _ in range(len(li)):
#     for i in range(len(li)-1):
#         if li[i] > li[i+1]:
#             li[i],li[i+1]=li[i+1],li[i]
# print(li)

# def quick_sort(arr):
#     if len(arr)<=1:
#         return arr
#     else:
#         pivot = arr[0]
#         left = [x for x in arr[1:] if x < pivot]
#         right = [x for x in arr[1:] if x >= pivot]
#         return quick_sort(left) + [pivot] + quick_sort(right)
# print(quick_sort([3,43,54,534,52354,1425,345,34532,32,23,2,33]))