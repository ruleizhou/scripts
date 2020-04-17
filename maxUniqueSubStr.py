# coding=utf-8
# 基于conda env:py35
# abcabfdbbad
import sys

if len(sys.argv) < 1:
    print('no param')
    exit()
print('params:' + str(sys.argv[1:]))

paramStr = str(sys.argv[1])
paramStrLen = len(paramStr)
df = [[0 for y in range(paramStrLen)] for x in range(paramStrLen)]
for x in range(paramStrLen):
    for y in range(x + 1, paramStrLen):
        notFound = int(paramStr[(y - 1 - df[x][y - 1]):y].find(paramStr[y]) < 0)
        df[x][y] = (df[x][y - 1] + 1) if notFound else 0

print('cal matrix:')
for i in range(paramStrLen):
    print(df[i])
maxNum = max(map(max, df))
print('max len：', maxNum)
print('max str:\n' + str(
    list([paramStr[x:y + 1] for x in range(paramStrLen) for y in range(x + 1, paramStrLen) if df[x][y] == maxNum])))
