# MC³ C4 - Arbitrary number of for loop executions instead of while
numList = []
for i in range(9999):
    a = int(input())
    if a == 0:
        break
    numList.append(a)

# MC³ C2 - Redundant or unnecessary loop
numMax = max(numList)
for j in range(1):
    print(numMax)

# MC³ C8 - for loop having its iteration variable overwritten
for k in range(numMax):
    print(k + 1)
    k += 2

# MC³ C1 - while condition tested again inside its block
while numMax != 0:
    print(numMax)
    numMax = numMax - 1
    if numMax == 0:
        break

# MC³ H1 - Statement with no effect
if numMax % 2 == 0:
    print(numMax, "is even")
else:
    True