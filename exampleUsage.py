from VisitorMC3 import *
import ast

# Constants that require instructor's expertise

C4_MAX_ALLOWED_RANGEITER = 50       # Maximum allowed constant within range() declarations
E2_MAX_ALLOWED_LISTS = 10           # Maximum allowed declared lists
G4_MIN_VAR_CHRS = 4                 # Minimum required characters in variable names
G4_MIN_FNC_CHRS = 8                 # Minimum required characters in function names
G4_MAX_ALLOWED_NONSIGNIFICANT = 70  # Maximum allowed non-significant names

# Reading and parsing the code to be analyzed
with open('testCode.py', 'r') as file:
    code = file.read()

parsed = ast.parse(code)

# Instantiating the NodeVisitor and detecting each MC³
visitor = VisitorMC3()
try:
    resA4 = visitor.getA4(parsed)

    resB6 = visitor.getB6(parsed)
    resB8 = visitor.getB8(parsed)
    resB9 = visitor.getB9(parsed)
    resB12 = visitor.getB12(parsed)

    resC1 = visitor.getC1(parsed)
    resC2 = visitor.getC2(parsed)
    resC4 = visitor.getC4(parsed, C4_MAX_ALLOWED_RANGEITER)
    resC8 = visitor.getC8(parsed)

    resD4 = visitor.getD4(parsed)

    resE2 = visitor.getE2(parsed, E2_MAX_ALLOWED_LISTS)

    resG4 = visitor.getG4(parsed, G4_MIN_VAR_CHRS, 
                          G4_MIN_FNC_CHRS, G4_MAX_ALLOWED_NONSIGNIFICANT)

    resG5 = visitor.getG5(parsed)

    resH1 = visitor.getH1(parsed)

except Exception as e:
    print(e)

# Printing the detected MC³
finally:
    res = [('A4', resA4[0]), ('B6', resB6), ('B8', resB8), ('B9', resB9), ('B12', resB12), 
           ('C1', resC1), ('C2', resC2), ('C4', resC4), ('C8', resC8), ('D4', resD4), 
           ('E2', resE2), ('G4', resG4), ('G5', resG5), ('H1', resH1)]
    
    for mc3 in res:
        if mc3[1]:
            print(f"I have detected MC³ {mc3[0]} in the code")