str1 = 'aaaabbcccdaa'
output = ''
char = str1[0]
count = 0 
for i in str1:
    if i==char:
        count+=1
    else:
        output= output+str(count)+char
        char = i
        count = 1
output= output+str(count)+char
print (output)