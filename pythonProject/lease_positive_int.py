def find_least_positive_integer(lst):
    num_set = set(lst)
    print (num_set)
    i = 1
    while i in num_set:
        i += 1
    return i

list1 = [1,2,4,5,6,-1,-3,100]
print(find_least_positive_integer(list1))