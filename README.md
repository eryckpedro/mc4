# Misconceptions in Correct Code Checker (MC4)

This is a public repository for MC4, a Python automated detection tool. MC4 uses static analysis to identify coding behaviors that indicate faulty or incomplete understandings of CS1 concepts, even in code that produces the expected results. These coding behaviors are termed *Misconceptions in Correct Code* (MC³).

## What are Misconceptions in Correct Code (MC³)?

MC³ refers to coding behaviors observed in novice programmers' code that may suggest an incomplete or faulty comprehension of concepts taught in CS1 courses. These misconceptions were identified in Python but can occur in other imperative programming languages.

For more details, refer to the [article on MC³](https://doi.org/10.5753/rbie.2023.3552).

## How does it work?

MC4 performs static code analysis using Python's AST (Abstract Syntax Tree) module. It checks the code after it has been parsed but before it is compiled to byte code. Therefore, the code must be parsable without errors for MC4 to analyze it.

## Target Audience

Currently, MC4 is best suited for CS1 instructors or teaching assistants to further assess students' code that already produces the expected outcome. MC4 does not yet provide formative feedback to assist CS1 students in improving their code.

## Currently Detectable MC³

MC4 can detect the following MC³. Note that some detections may require the expertise of an instructor or teaching assistant to determine if the misconception is present in the code.

- **A4 - Redefinition of built-in**: occurs when a student mistakenly names a variable or function with the same name as a Python built-in function (e.g., ```max```).

- **B6 - Boolean comparison attempted with ```while``` loop**: occurs when students attempt to create a basic comparison statement using a ```while``` loop instead of appropriate conditional commands.

- **B8 - Non utilization of ```if/else``` statement**: occurs when students declare a sequence of ```if-elif``` statements without including a concluding ```else``` clause.

- **B9 - ```elif/else``` retesting already checked conditions**: occurs when students declare an ```elif``` statement checking the opposite condition of a previously declared ```if``` or ```elif``` statement.

 - **B12 - Consecutive equal ```if``` statements with distinct operations in their blocks**: occurs when students declare two or more ```if``` statements that test the same condition, albeit executing different commands in each block.

- **C1 - ```while``` condition tested again inside its block**: occurs when students declare a ```while``` loop and, at the end of its body, also include an ```if``` statement to verify if the ```while``` condition has become false, ending the loop with a ```break``` statement.

- **C2 - Redundant or unnecessary loop**: occurs when students declare a ```while``` or ```for``` loop that executes only once.

- **C4 - Arbitrary number of ```for``` loop executions instead of ```while```**: occurs when students declare a ```for``` loop to execute an excessively high number of iterations, aiming to replicate the functionality of a ```while``` loop. The automated detection requires the user to set the threshold to consider how many ```for``` loop iterations are needed to be present to flag the MC³.

- **C8 - ```for``` loop having its iteration variable overwritten**: occurs when students reassign the value of the iteration variable of a ```for``` loop inside the loop’s body.

- **D4 - Function accessing variables from outer scope**: occurs when students declare functions that attempt to access variables that are not present in the function's scope.

- **E2 - Redundant or unnecessary use of lists**: occurs when students excessively depend on lists as a solution for various programming problems. The automated detection requires the user to set the threshold to consider how many user-declared lists are needed to be present to flag the MC³.

- **G4 - Functions/variables with non-significant name**: occurs as consequence of students using arbitrary names for variables and functions in their code. The automated detection requires the user to set a minimum character length for variables and function names. The MC³ is flagged if a percentage of total variables or functions that does not match the length criteria is met. This percentage is also defined by the instructor.

- **G5 - Arbitrary organization of declarations**: occurs when students structure their code arbitrarily, with functions declared interchangeably with other statements.

- **H1 - Statement with no effect**: occurs when students include code in their programs that has no effect on the program's execution (e.g. lone ```True``` statements).

## Utilization

The automated detection is implemented as a class in the file `VisitorMC3.py`. You need to import it into your working file to use it.

You can use the file `exampleUsage.py` as a template. It demonstrates how a Python `.py` file should be parsed before the automated detection can be performed. You need to instantiate a visitor by calling the `VisitorMC3()` constructor. All detections will be performed based on this instantiated visitor.

Each MC³ is detected via a method called `visitor.getXX()`, in which `XX` is the MC³'s name. Each detection method requires the parsed object of the Python code. Some MC³ may also require constants defined by the instructor or teaching assistant. These constants are presented in the `exampleUsage.py` file.

The files ```testCodeA.py```, ```testCodeB.py```, and ```testCodeC.py``` were elaborated to present code snippets that MC4 can detect.

Each detection method returns `True` if the checked code contains the MC³, or `False` otherwise. Multiple detections of the **same** MC³ in the **same** code are ignored.

## Limitations

There are several limitations in MC4's automated detection. These limitations are documented in each method within the `VisitorMC3` class.

## Disclaimer

MC4 is a tool developed for academic purposes. It was initially conceived to assist in the development of a Ph.D. thesis. This project was partially funded by Fundação de Desenvolvimento da UNICAMP (FUNCAMP) and by the Brazilian National Council for Scientific and Technological Development (CNPq).

## License

GNU General Public License (GPL)
