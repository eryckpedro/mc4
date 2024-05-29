num1 = int(input())
num2 = int(input())

sum = num1 + num2

while sum > 9:
    print(sum, "has more than one digit")
    break

if num2 <= 0:
    res = num1 * num2
if num2 % 2 == 0:
    res = num1 ** num2

if num1 % 2 == 0:
    print(num1, "is even")
elif num2 % 2 == 0 and num1 % 2 != 0:
    print(num2, "is even", num1, "is odd")

if num1 == num2 * 2:
    print(num1, "is multiple of", num2)
if num1 == num2 ** 2:
    print(num1, "is even")

