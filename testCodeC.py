# MC³ E2 - Redundant or unnecessary use of lists
sides1 = [float(i) for i in input().split()]
sides2 = [float(i) for i in input().split()]
sides3 = [float(i) for i in input().split()]
sides4 = [float(i) for i in input().split()]
sides5 = [float(i) for i in input().split()]

# MC³ G5 - Arbitrary organization of declarations
def SumCoordinates():
    sidesSummed = []
    length = len(sides1) # MC³ D4 - Function accessing variables from outer scope

    for i in range(length):
        sidesSummed.append(sides1[i] + sides2[i] + sides3[i] + sides4[i] + sides5[i])
    
    return sidesSummed

print(SumCoordinates())