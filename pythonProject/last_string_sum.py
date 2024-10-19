str1 = 'aabcccccaaa'
out = 'a2b1c5a3'
char = str1[0]
count = 0
output  = ''
for i in str1:
    if i==char:
        count+=1
    else:
        output = output+char+str(count)
        char = i
        count = 1
output = output+char+str(count)
print(output)

str1  = '4a2v'
output  = ''
char = str1[0]
for i in str1:
    if not i.isalpha():
        f = i
    else:
        output =  output+int(f)*i
print(output)
