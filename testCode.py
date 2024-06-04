# MC³ G4 - Functions/variables with non significant name
num1 = int(input())
num2 = int(input())

# MC³ A4 - Redefinition of built-in
sum = num1 + num2                           

# MC³ B6 - Boolean comparison attempted with while loop
while sum > 9:                              
    print(sum, "has more than one digit")
    break

# MC³ B8 - Non utilization of elif/else statement
if num1 % 2 == 0:
    print(num1, "is even")
elif num1 % 2 == 1:
    print(num1, "is odd")

# MC³ B9 - elif/else retesting already checked conditions
if num1 < 0:
    print(num1, "is negative")
elif num2 < 0 and num1 >= 0:
    print(num2, "is negative", num1, "is non-negative")

# MC³ B12 - Consecutive equal if statements with distinct operations in their blocks
doubleCond = num1 == num2 * 2

if doubleCond:
    print(num1, "is multiple of", num2)
if doubleCond:
    print(num1, "is even")

