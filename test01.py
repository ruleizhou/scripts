# coding=utf-8
# 基于conda env:py35
# abcabfdbbad
tmpStr = 'abcabfdbbad'
lenStr = len(tmpStr)
df = [[0 for y in range(lenStr)] for x in range(lenStr)]
for x in range(lenStr):
    for y in range(x + 1, lenStr):
        print(str(x), str(y))
        print(df[x])
        print(tmpStr[(y - 1 - df[x][y - 1]):y + 1])
        notFound = int(tmpStr[(y - 1 - df[x][y - 1]):y].find(tmpStr[y]) < 0)
        df[x][y] = (df[x][y - 1] + 1) if notFound else 0

for i in range(lenStr):
    print(df[i])
