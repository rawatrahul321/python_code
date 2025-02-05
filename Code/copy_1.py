from copy import copy,deepcopy
li = [1,2,3,4]
li1 = copy(li)
li1[2] = 33
li1.append(22)
print(li,"li")
print(li1,"li1")
li2 = deepcopy(li)
li2[2]=44
li2.append(11)
print(li,"li")
print(li2,"li2")
