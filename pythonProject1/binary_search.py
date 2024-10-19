# Insertion sort in Python
def insertionSort(arr):
    for i in range(1,len(arr)):
        j = i
        while j>0 and arr[j-1]>arr[j]:
            arr[j-1],arr[j]=arr[j],arr[j-1]
            j-=1
data = [9, 5, 1, 4, 3]
insertionSort(data)
print('Sorted Array in Ascending Order:')
print(data)


# Selection sort in Python
def selectionSort(arr):
    for i in range(len(arr)):
        min_id = i
        for j in range(i+1,len(arr)):
            if arr[j]<arr[min_id]:
                min_id = j
        arr[i],arr[min_id]=arr[min_id],arr[i]
    print(arr)
arr = [-2, 45, 0, 11, -9]
selectionSort(arr)

lst = [1, 2, 3, 3, 5]
def binary_search_max(lst):
    low, high = 0, len(lst) - 1
    while low < high:
        mid = (low + high) // 2
        if lst[mid] < lst[high]:
            low = mid + 1
        else:
            high = mid
    return lst[low]
print(binary_search_max(lst))


# arr  = [1,2,3,3,3,3,4,5,4,5]
# def binary_lower_bond(arr,target):
#     left = 0
#     right = len(arr)-1
#     lb = len(arr)
#     while left<=right:
#         mid = (left+right)//2
#         if arr[mid]>=target:
#             lb = mid
#             right = mid-1
#         else:
#             left = mid +1
#     return lb
# print(binary_lower_bond(arr,3))
# def binary_upper_bond(arr,target):
#     left = 0
#     right = len(arr)-1
#     ub = 0
#     while left<=right:
#         mid = (left+right)//2
#         if arr[mid]>target:
#             ub = mid
#             right = mid -1
#         else:
#             left = mid +1
#     return ub
# print(binary_upper_bond(arr,3))
# def feq_occur(arr):
#     return binary_upper_bond(arr,3)-binary_lower_bond(arr,3)
# print(feq_occur(arr))

# def merge_sort(arr):
#     if len(arr)<=1:
#         return arr
#     mid = len(arr)//2
#     lefthalf = arr[:mid]
#     righthalf = arr[mid:]
#     sortedleft = merge_sort(lefthalf)
#     sortedright = merge_sort(righthalf)
#     return merge(sortedleft,sortedright)
# def merge(left,right):
#     result  = []
#     i=j=0
#     while i<len(left) and j<len(right):
#         if left[i]<right[j]:
#             result.append(left[i])
#             i+=1
#         else:
#             result.append(right[j])
#             j+=1
#     result.extend(left[i:])
#     result.extend((right[j:]))
#     return result
# print(merge_sort([3, 7, 6, -10, 15, 23.5, 55, -13]))


# import math
# def binary_search(li, element):
#     left = 0
#     right = len(li) - 1
#     index = -1
#     while right >= left and index == -1:
#         mid = int(math.floor((right + left) / 2))
#         if li[mid] == element:
#             print(li[mid],mid,element)
#             index = mid
#
#         elif li[mid] > element:
#             right = mid - 1
#             print(right,"right")
#         else:
#             left = mid + 1
#             print(left,"left")
#     return index
#
#
# print(binary_search([ 5, 6, 7, 8, 9], 8))
# # print(binary_search([ 1, 2, 3, 12, 34], 34))
#
# def binary_search(n,target):
#     left = 0
#     right = len(n)-1
#     while left<right:
#         mid = (right+left)//2
#         if n[mid]==target:
#             return mid
#         elif n[mid]>target:
#             right = mid-1
#         else:
#             left = mid+1
#     return -1
#
# print(binary_search([ 4,5, 6, 7, 8,9], 8))
