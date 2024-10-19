arr  = [1,2,3,3,3,3,4,5,4,5]
def binary_max_occur(arr,target):
    left = 0
    right = len(arr)-1
    lb = len(arr)
    while left<=right:
        mid = (left+right)//2
        if arr[mid]>=target:
            lb = mid
            right = mid-1
        else:
            left = mid +1
    return lb
print(binary_max_occur(arr,3))

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
#     while left<=right:
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
