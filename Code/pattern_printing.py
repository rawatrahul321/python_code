n=int(input("enter the number:"))
row_column = (2*n)-1
l = 0
m = row_column-1
val = n
custom_row_column = [[0 for i in range(row_column)] for j in range(row_column)]
for i in range(n):
    for j in range(l,m+1):
        custom_row_column[i][j] = val
    for j in range(l+1,m+1):
        custom_row_column[j][i] = val
    for j in range(l+1,m+1):
        custom_row_column[m][j] = val
    for j in range(l+1,m):
        custom_row_column[j][m] = val
    l = l+1
    m = m-1
    val = val-1
for i in range(row_column):
    for j in range(row_column):
        print(custom_row_column[i][j],end= ' ')
    print()