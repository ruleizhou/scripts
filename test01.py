# coding=utf-8
# 基于conda env:py35

tmpStr = 'abcabfdbbad'
lenStr = len(tmpStr)
df = [[1 for y in range(lenStr)] for x in range(lenStr)]
for x in range(lenStr):
    for y in range(x + 1, lenStr):
        print(str(x), str(y))
        find = int(tmpStr[y - df[x][y - 1]:y + 1].find(tmpStr[y]) < 0)
        df[x][y] = (df[x][y - 1] + 1) if find else 1

for i in range(lenStr):
    print(df[i])
