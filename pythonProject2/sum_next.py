arr = [-9,-1,1,3,2,8,11]
left = 0
right = len(arr) - 1

while left<right:
    sum = arr[left] + arr[right]
    if sum==0:
        print(arr[left],arr[right])
        break
    elif sum<0:
        left +=1
    else:
        right -=1

# num = '57'
# sum = 0
# sum_next = 0
# for i in num:
#     sum+=int(i)
# for i in str(sum):
#     sum_next+=int(i)
   
# print(sum)
# print(sum_next)