import ast

class VisitorMC3(ast.NodeVisitor):
    def __init__(self):
        self.builtinRedefinition = False
        self.declaredVariablesAsBuiltIn = []
        self.declaredFunctionsAsBuiltin = []
        self.declaredArgumentsAsBuiltin = []

        self.boolOpAttemptedWithWhile = False
        self.nonUtilizationElifElse = False
        self.elifRetestingCondition = False
        self.consecutiveEqualIfs = False
        
        self.whileCondInItsBody = False
        self.redundantLoop = False
        self.forWithConstant = False
        self.forVariableOverwritten = False

        self.varOutsideFuncScope = False

        self.listOverusage = False

        self.nonSignificantNames = False
        self.arbitraryDeclarations = False

        self.noEffectStatement = False

    def checkBuiltInRedefinition(self, root):
        """Designed as a counter for A4 - Redefinition of built-in.
           
           Checks the whole tree checking if any declared variable, function
           name or function argument is within Python's list of built-ins.

           Rationale: Python lets its users to redefine built-in functions, but,
           considering an CS1 scope, the student is probably doing this unintentionally.
           Thus, it would be best if they are alerted about this practice.
        """
        list_of_builtins = ['abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes', 
                            'callable', 'chr', 'classmethod', 'compile', 'complex', 'delattr',
                            'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter',
                            'float', 'format', 'frozenset', 'getattr', 'global', 'hasattr',
                            'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance', 'issubclass',
                            'iter', 'len', 'list', 'locals', 'map', 'max', 'memoryview', 'min', 'next',
                            'object', 'oct', 'open', 'ord', 'pow', 'print', 'property', 'range', 'repr',
                            'reversed', 'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod',
                            'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip']

        #Declared variables
        for node in ast.walk(root):
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name): #direct assign to a variable e.g. bool = (...)
                        if tgt.id in list_of_builtins and tgt.id not in self.declaredVariablesAsBuiltIn:
                                self.declaredVariablesAsBuiltIn.append(tgt.id)

                    if isinstance(tgt, ast.Tuple): #unpacking e.g. max, bool = (...)
                        for name in tgt.elts:
                            if isinstance(name, ast.Subscript): #ignores Subscripts e.g. list[0] = (...)
                                continue

                            if name.id in list_of_builtins and name.id not in self.declaredVariablesAsBuiltIn:
                                self.declaredVariablesAsBuiltIn.append(name.id)


        #Declared function names
        for node in ast.walk(root):
            if isinstance(node, ast.FunctionDef):
                if node.name in list_of_builtins and node.name not in self.declaredFunctionsAsBuiltin:
                    self.declaredFunctionsAsBuiltin.append(node.name)
        
        #Arguments in declared function names
        for node in ast.walk(root):
            if isinstance(node, ast.FunctionDef):
                for arguments in ast.iter_child_nodes(node):
                    for arg in ast.iter_child_nodes(arguments):
                        if isinstance(arg, ast.arg):
                            if arg.arg in list_of_builtins and arg.arg not in self.declaredArgumentsAsBuiltin:
                                self.declaredArgumentsAsBuiltin.append(arg.arg)
        
        if len(self.declaredVariablesAsBuiltIn) + \
           len(self.declaredFunctionsAsBuiltin) + \
           len(self.declaredArgumentsAsBuiltin) > 0:
            self.builtinRedefinition = True

    def checkBooleanAttemptedWithWhile(self, root):
        """Designed as a counter for B6 - Boolean comparison attempted with 
           while loop.
           
           Checks the whole tree for a While loop that has a comparison made as
           its test but also has a loose Break statement within its body.

           Rationale: if the code has a While loop with a comparison as its test
           and a loose Break statement within its body, it probably means that
           students are trying to use the While loop as an If-statament. This MC³
           is a special case of C2 - Redundant or unnecessary loop.
        """
        for node in ast.walk(root):
            if isinstance(node, ast.While):
                if isinstance(node.test, ast.Compare) or isinstance(node.test, ast.BoolOp):
                    for item in node.body:
                        if isinstance(item, ast.Break):
                            self.boolOpAttemptedWithWhile = True
    
    def checkNonUtilizationElifElse(self, root):
        """Designed as a counter for B8 - Non utilization of elif/else.
           
           Checks the whole tree for two situations that can indicate a non
           utilization of elif/else statements: 1) the code has an Elif statement
           without a following Else; and 2) the code has multiple, consecutive If
           statements. Currently only 1) is implemented.
            
           Rationale: for 1), if the code has Elif statements but no ending Else,
           there is a chance the student is forgetting a base case to the comparison.
           Regarding 2), if there are multiple, consecutive If statements in the code,
           there is a chance the student is either disconfortable with using Elif/Else
           statements and a small further chance that the code can execute consecutive
           Ifs when it is not intended to. There are false positive cases for 1) and 2),
           but it's better to flag 'em out to the student nonetheless.
        """

        def checkElifWithoutElse(root):
            """This checks if there is an If, followed by an Elif without an Else.

               It uses the orelse field present in each If statement. In the case of
               an Elif, there is an immediate If statement in the parent orelse. However,
               this can trigger false positives when an If is immediately used inside 
               an Else.
            """
            for node in ast.walk(root):
                if isinstance(node, ast.If):
                    if len(node.orelse) > 0:
                        if isinstance(node.orelse[0], ast.If):
                            if len(node.orelse[0].orelse) == 0:
                                self.nonUtilizationElifElse = True

        checkElifWithoutElse(root)

    def checkElifRetestingCondition(self, root):
        """Designed as a counter for B9 - elif/else retesting already checked 
           conditions.
           
           Checks the whole tree for an If/Elif statement that has a single Compare 
           node (e.g. if a > 0) that is followed by Elif stataments in which the
           opposite comparison is made (e.g. elif a <= 0). While searching for
           the opposite comparisons, this methods checks BinOps until a Compare node
           is reached, thus comparing with the original statement. Will also work with
           If statements declared in the Else block of the first If analyzed.

           Rationale: if the student declares an Elif/Else checking the opposite
           comparison made in an above If statement, this second check is unnecessary
           because of the Elif syntax.
        """

        def compareLeft(node1, node2):
            """Helper function that compares the left side of two If tests.
            """
            if isinstance(node1, ast.Name) and isinstance(node2, ast.Name):
                return node1.id == node2.id

            return False
        
        def compareOps(node1, node2):
            """Helper function that compares the operation of two If tests. It
            returns True if they are opposite.
            """
            invOp = {ast.Eq: ast.NotEq,
                     ast.NotEq: ast.Eq,
                     ast.Lt: ast.GtE,
                     ast.LtE: ast.Gt,
                     ast.Gt: ast.LtE,
                     ast.GtE: ast.Lt,
                     ast.In: ast.NotIn,
                     ast.NotIn: ast.In,
                     ast.Is: ast.IsNot,
                     ast.IsNot: ast.Is}

            if len(node1) == len(node2) == 1:
                return invOp[type(node1[0])] == type(node2[0])

            return False
        
        def compareRight(node1, node2):
            """Helper function that compares the right side of two If tests.
            """
            if len(node1) == len(node2) == 1:
                if isinstance(node1[0], ast.Constant) and isinstance(node2[0], ast.Constant):
                    return node1[0].value == node2[0].value
                
                if isinstance(node1[0], ast.Name) and isinstance(node2[0], ast.Name):
                    return node1[0].id == node2[0].id

                return False
            return False

        def compareElifsR(node, mainLeft, mainOps, mainCps):
            '''Helper function that recursively traverses through all Elif/Else
               and checks if any of their Compare nodes tests the opposite
               comparison of the first Compare node identified in the prime If
               statement.
            '''

            if isinstance(node, ast.Compare):
                if compareLeft(mainLeft, node.left) and \
                   compareOps(mainOps, node.ops) and \
                   compareRight(mainCps, node.comparators):
                    self.elifRetestingCondition = True
            
            if isinstance(node, ast.BoolOp):
                for chd in node.values:
                    compareElifsR(chd, mainLeft, mainOps, mainCps)


        for node in ast.walk(root):
            if isinstance(node, ast.If):
                if len(node.orelse) > 0 and isinstance(node.test, ast.Compare):
                    mainIfL = node.test.left
                    mainIfOps = node.test.ops
                    mainIfCps = node.test.comparators

                    for chd in node.orelse:
                        if isinstance(chd, ast.If):
                            compareElifsR(chd.test, mainIfL, mainIfOps, mainIfCps)

    def checkConsecutiveIfs(self, root):
        """Designed as a counter for B12 - Consecutive equal if statements with 
           distinct operations in their blocks.
           
           Checks the whole tree for two consecutive equal If statements. Currently
           only works with If statements in which the test is either an ast.Name
           (e.g. "if a") or a single ast.Compare node (e.g. "if a > 2").
            
           Rationale: if the code has two (or more) consecutive equal If statements,
           the student is probably dividing a rationale for a single If in multiple
           If's, but they can be declared inside a single If block.
        """
        def compareLeft(node1, node2):
            """Helper function that compares the left side of the 1st and 2nd
               If tests.
            """
            if isinstance(node1, ast.Name) and isinstance(node2, ast.Name):
                return node1.id == node2.id

            return False
        
        def compareOps(node1, node2):
            """Helper function that compares the operation used in the While test 
               and the If test.
            """
            if len(node1) == len(node2) == 1:
                return node1[0] == node2[0]
            
            return False
        
        def compareRight(node1, node2):
            """Helper function that compares the right side of the 1st and 2nd
               If tests.
            """
            if len(node1) == len(node2) == 1:
                if isinstance(node1[0], ast.Constant) and isinstance(node2[0], ast.Constant):
                    return node1[0].value == node2[0].value
                
                if isinstance(node1[0], ast.Name) and isinstance(node2[0], ast.Name):
                    return node1[0].id == node2[0].id

                return False
            return False

        for node in ast.walk(root):
            conseqIf = False
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.If) and conseqIf is False:
                    if len(child.orelse) == 0:  #checking if there are no elifs
                        conseqIf = True
                        firstIf = child
                elif isinstance(child, ast.If) and conseqIf is True:
                    if len(child.orelse) == 0:  #checking if there are no elifs
                        secondIf = child

                        if isinstance(firstIf.test, ast.Name) and isinstance(secondIf.test, ast.Name):
                            if firstIf.test.id == secondIf.test.id:
                                self.consecutiveEqualIfs = True

                        if isinstance(firstIf.test, ast.Compare) and isinstance(secondIf.test, ast.Compare):
                            L = compareLeft(firstIf.test.left, secondIf.test.left)
                            O = compareOps(firstIf.test.ops, secondIf.test.ops)
                            R = compareRight(firstIf.test.comparators, secondIf.test.comparators)

                            if L and O and R: 
                                self.consecutiveEqualIfs = True

                    conseqIf = False
                else:
                    conseqIf = False

    def checkWhileCondInItsBody(self, root):
        """Designed as a counter for C1 - While condition tested again inside 
           its block.
           
           Checks the whole tree for a While loop that has its test condition
           tested again inside its block in order to break the loop. This means
           that the inside test is composed as the inverse of test used in the
           While loop. Currently only works with comparisons of two variables
           or one variable and one constant.

           Rationale: if the code has a While condition that has the inverse of
           its test tested again inside its block, it probably means the interior
           test is redundant and can be expressed in other ways.
        """
        def compareLeft(node1, node2):
            """Helper function that compares the left side of the While test and
               the If test.
            """
            if isinstance(node1, ast.Name) and isinstance(node2, ast.Name):
                return node1.id == node2.id

            return False
        
        def compareOps(node1, node2):
            """Helper function that compares the operation used in the While test 
               and the If test.
            """
            invOp = {ast.Eq: ast.NotEq,
                     ast.NotEq: ast.Eq,
                     ast.Lt: ast.GtE,
                     ast.LtE: ast.Gt,
                     ast.Gt: ast.LtE,
                     ast.GtE: ast.Lt,
                     ast.In: ast.NotIn,
                     ast.NotIn: ast.In,
                     ast.Is: ast.IsNot,
                     ast.IsNot: ast.Is}

            if len(node1) == len(node2) == 1:
                return invOp[type(node1[0])] == type(node2[0])

            return False
        
        def compareRight(node1, node2):
            """Helper function that compares the right side of the While test and
               the If test.
            """
            if len(node1) == len(node2) == 1:
                if isinstance(node1[0], ast.Constant) and isinstance(node2[0], ast.Constant):
                    return node1[0].value == node2[0].value
                
                if isinstance(node1[0], ast.Name) and isinstance(node2[0], ast.Name):
                    return node1[0].id == node2[0].id

                return False
            return False

        for node in ast.walk(root):
            if isinstance(node, ast.While):
                if isinstance(node.test, ast.Compare):
                    for item in node.body:
                        if isinstance(item, ast.If):
                            if isinstance(item.test, ast.Compare):
                                L = compareLeft(node.test.left, item.test.left)
                                O = compareOps(node.test.ops, item.test.ops)
                                R = compareRight(node.test.comparators, item.test.comparators)

                                if L and O and R: 
                                    self.whileCondInItsBody = True

    def checkRedundantLoop(self, root):
        """Designed as a counter for C2 - Redundant or unnecessary loop.
           
           Checks the whole tree for a loop that only executes once. This means
           a For loop with a range(1) or a While-True loop that executes once 
           using a loose Break statement within its body.

           Rationale: if the code has a loop that executes only once than there is
           no need for said loop. The While scenario can be possibly interpreted as
           B6 - Boolean comparison attempted with While loop.
        """
        def checkWhile(root):
            """Helper function that checks if a While loop has a loose break within 
               its body.
            """
            for node in ast.walk(root):
                if isinstance(node, ast.While):
                    if isinstance(node.test, ast.Constant):
                        if node.test.value is True:
                            for item in node.body:
                                if isinstance(item, ast.Break):
                                    #print("While-True-Break", end="")
                                    self.redundantLoop = True
        
        def checkFor(root):
            """Helper function that checks if a For loop uses a range(1).
            """
            hasRange = hasConstant = False
            for node in ast.walk(root):
                if isinstance(node, ast.For):
                    if isinstance(node.iter, ast.Call):
                        if isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                            hasRange = True
                            if len(node.iter.args) == 1:
                                if isinstance(node.iter.args[0], ast.Constant):
                                    if node.iter.args[0].value == 1:
                                        hasConstant = True

            if hasRange is True and hasConstant is True:
                #print("for-range(1)", end="")
                self.redundantLoop = True
        
        checkWhile(root)
        checkFor(root)

    def checkForWithConstant(self, root, constThreshold = 1):
        """Designed as a counter for C4 - Arbitrary number of for loop execution 
           instead of while.
           
           Checks the whole tree for a for loop that has a range function with a
           constant as its parameter and checks if that constant is greater or equal
           than the specified threshold. Will only work with constants. If no
           threshold is specified, the method considers all that are greater or
           equal to 1.

           Rationale: if the code has a for loop with a constant in the range
           function and this constant is a big number, C4 might be present. 
           However, since there is no clear definition of what a "big number" is, 
           it's better to let the instructor decide by passing the threshold as an
           argument.
        """

        for node in ast.walk(root):
            if isinstance(node, ast.For):
                if isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                        if len(node.iter.args) == 1:
                            if isinstance(node.iter.args[0], ast.Constant):
                                if node.iter.args[0].value >= constThreshold:
                                    self.forWithConstant = True

    def checkForOverwritten(self, root, prevIterVars):
        """Designed as a counter for C8 - for loop having its iteration variable 
           overwritten.
           
           Checks the whole tree if a for loop has its iteration variable reassigned
           within its body. It recursively checks iteration variables used in inner
           for loops.
            
           Rationale: the redefinition of for iteration variables may lead to bugs
           that are difficult to debug. This function will flag out if this is 
           happening in the code.
        """
        def getVarIter(node):
            """Helper function that checks a the target field of a for loop and 
            returns all its iteration variables. This will not work with nested
            tuples as iteration variables e.g. for (i, (j, k)) in (...).
            """
            varIter = []

            if isinstance(node.target, ast.Name):
                varIter.append(node.target.id)

            if isinstance(node.target, ast.Tuple) or isinstance(node.target, ast.List):
                for item in node.target.elts:
                    if isinstance(item, ast.Name):
                        varIter.append(item.id)
                
            return varIter
        
        def getVarIterR(node, varIter):
            """TO DO: IMPLEMENT A RECURSIVE METHOD THAT CHECKS NESTED TUPLE/LISTS"""
            if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
                varIter.append(node.target.id)
                return varIter
            
            if isinstance(node, ast.For) and (isinstance(node.target, ast.Tuple) or isinstance(node.target, ast.List)):
                for item in node.target.elts:
                    return getVarIterR(item, varIter)
            
            if isinstance(node, ast.Name):
                varIter.append(node.id)
                return varIter
            
            if isinstance(node.target, ast.Tuple) or isinstance(node.target, ast.List):
                for item in node.elts:
                    return getVarIterR(item, varIter)
        
        def checkAssigns(self, prevIterVars, varIter, item):
            """Helper function that iterates over an Assign Node in a for loop body 
               and checks if a iteration variable was overwritten.
            """
            for asg in item.targets:
                if isinstance(asg, ast.Name): #direct assignments e.g. i = (...)
                    for var in prevIterVars + varIter:
                        if asg.id == var:
                            self.forVariableOverwritten = True

                if isinstance(asg, ast.Tuple): #unpacking e.g. i, j = (...)
                    for name in asg.elts:
                        if isinstance(name, ast.Subscript): #ignores Subscripts e.g. list[0] = (...)
                            continue

                        for var in prevIterVars + varIter:
                            if name.id == var:
                                self.forVariableOverwritten = True

        for node in ast.walk(root):
            if isinstance(node, ast.For):

                varIter = getVarIter(node)

                for item in node.body:
                    for stm in ast.walk(item):
                        if isinstance(stm, ast.For): #checks nested for loops
                            self.checkForOverwritten(stm, prevIterVars + varIter)

                        if isinstance(stm, ast.Assign):
                            checkAssigns(self, prevIterVars, varIter, stm)

                        if isinstance(stm, ast.AugAssign): #augmented assigns e.g. i += 1
                            if isinstance(stm.target, ast.Subscript): #ignores Subscripts e.g. list[0] = (...)
                                continue

                            for var in varIter:
                                if stm.target.id == var:
                                    self.forVariableOverwritten = True

    def checkVarOutsideFuncScope(self, root):
        """Designed as a counter for D4 - Function accessing variables from outer 
           scope.
           
           Checks the whole tree if an user declared function uses variables that
           are not present in the said function's scope.

           Currently only works with:

           - Function Calls:
                + Simple variable names in called function arguments e.g. print(a)
            - Assignments:
                + Simple RHS name assignments e.g. (...) = a
                + Simple variable names in RHS called function assignments 
                  e.g (...) = round(a, 2)
                + Simple Subscripts in LHS and RHS e.g. a[0] = (...), (...) = b[0][0] 
            - AugAssignments:
                + Simple LHS and RHS names in augmented assignments e.g. a += b
            - Conditionals:
                + Simple If statements that use a single Compare node e.g. if a == b
                + Simple While statements that use a single Compare node e.g. while a >= b
            - Loops:
                + Simple For statements in which the Iter field is either an ast.Name or
                  ast.Call e.g. for (...) in range(a):, for (...) in b:
            
           Rationale: if an user declared function uses variables that are not
           passed as arguments nor declared in its body, those variables are from
           outer scope and this should be avoided.
        """
        def getGlobalVars(root):
            globalVars = []
            for node in ast.iter_child_nodes(root):
                if not isinstance(node, ast.FunctionDef):
                    for chd in ast.walk(node):
                        if isinstance(chd, ast.Assign):
                            for item in chd.targets:
                                if isinstance(item, ast.Name) and item.id not in globalVars:
                                    globalVars.append(item.id)

                                if isinstance(item, ast.Tuple):
                                    for elem in item.elts:
                                        if isinstance(elem, ast.Name) and elem.id not in globalVars:
                                            globalVars.append(elem.id)

            return globalVars

        
        def getLocalVars(funcNode, globalVars):
            localVars = []

            for arg in funcNode.args.args:
                if arg.arg not in localVars:
                    localVars.append(arg.arg)

            for stm in funcNode.body:
                if isinstance(stm, ast.Assign):
                    for item in stm.targets:
                        if isinstance(item, ast.Name) and item.id not in localVars:
                            localVars.append(item.id)
                            if item.id in globalVars:
                                self.varOutsideFuncScope = True
                        
                        if isinstance(item, ast.Tuple):
                            for elem in item.elts:
                                if isinstance(elem, ast.Name) and elem.id not in localVars:
                                    localVars.append(elem.id)
                                    if elem.id in globalVars:
                                        self.varOutsideFuncScope = True
            
            return localVars

        def iterateSubscript(node, localVars, globalVars):

            while not isinstance(node, ast.Name):

                if isinstance(node, ast.Attribute):
                    #Not covering Attributes of variables e.g. var.property
                    break
                
                if isinstance(node, ast.ListComp):
                    #Not covering List Comprehensions as Subscripts
                    break

                if isinstance(node, ast.Call):
                    #Checks if the value of a Subscript is a Function Call e.g. foo(x)[0]
                    for arg in node.args:
                        if isinstance(arg, ast.Name):
                            if arg.id in globalVars and arg.id not in localVars:
                                self.varOutsideFuncScope = True
                    break

                if isinstance(node, ast.Tuple):
                    #Checks if the value of a Subscript is a Tuple e.g. (a, b, c)[0]
                    for item in node.elts:
                        if isinstance(item, ast.Name):
                            if item.id in globalVars and item.id not in localVars:
                                self.varOutsideFuncScope = True
                    break
                            

                if isinstance(node, ast.Subscript):
                    #Checks simple indexes e.g. <var>[<var>] = (...)
                    if isinstance(node.slice, ast.Index):
                        if isinstance(node.slice.value, ast.Name):
                            if node.slice.value.id in globalVars and node.slice.value.id not in localVars:
                                self.varOutsideFuncScope = True

                        node = node.value
                    else: #Not covering Slice and ExtSlice e.g. a[1:2] or a[1:2, 3]
                        break
            
            if isinstance(node, ast.Name):
                if node.id in globalVars and node.id not in localVars:
                    self.varOutsideFuncScope = True

        def testFunctionCall(stm, localVars, globalVars):
            if isinstance(stm, ast.Expr):
                if isinstance(stm.value, ast.Call):

                    #Attributes's values e.g. <var>.append((...))
                    if isinstance(stm.value.func, ast.Attribute):
                        if isinstance(stm.value.func.value, ast.Name):
                            if stm.value.func.value.id in globalVars and stm.value.func.value.id not in localVars:
                                self.varOutsideFuncScope = True

                    #FunctionCall's arguments e.g. print(<var>), (...).append(<var>)
                    for arg in stm.value.args:
                        if isinstance(arg, ast.Name):
                            if arg.id in globalVars and arg.id not in localVars:
                                self.varOutsideFuncScope = True

        
        def testAssign(stm, localVars, globalVars):
            if isinstance(stm, ast.Assign):

                #Assign's LHS e.g. <var> = (...)
                for item in stm.targets:

                    if isinstance(item, ast.Subscript):
                        iterateSubscript(item, localVars, globalVars)

                    if isinstance(item, ast.Name):
                        if item.id in globalVars and item.id not in localVars:
                            self.varOutsideFuncScope = True
                    
                    if isinstance(item, ast.Tuple):
                        for elem in item.elts:
                            if isinstance(elem, ast.Name) and elem.id in globalVars and elem.id not in localVars:
                                self.varOutsideFuncScope = True

                #Assign's RHS e.g. (...) = <var>
                if isinstance(stm.value, ast.Subscript):
                    iterateSubscript(stm.value, localVars, globalVars)

                if isinstance(stm.value, ast.Name):
                    if stm.value.id in globalVars and stm.value.id not in localVars:
                        self.varOutsideFuncScope = True
                
                if isinstance(stm.value, ast.Tuple):
                    for elem in stm.value.elts:
                        if isinstance(elem, ast.Name) and elem.id in globalVars and elem.id not in localVars:
                            self.varOutsideFuncScope = True
                
                if isinstance(stm.value, ast.Call):
                    for arg in stm.value.args:
                        if isinstance(arg, ast.Name):
                            if arg.id in globalVars and arg.id not in localVars:
                                self.varOutsideFuncScope = True

        def testAugAssign(stm, localVars, globalVars):
            if isinstance(stm, ast.AugAssign):
                if isinstance(stm.target, ast.Name):
                    if stm.target.id in globalVars and stm.target.id not in localVars:
                        self.varOutsideFuncScope = True

                if isinstance(stm.value, ast.Name):
                    if stm.value.id in globalVars and stm.value.id not in localVars:
                        self.varOutsideFuncScope = True

        def testConditionals(stm, localVars, globalVars):
            if isinstance(stm, ast.If) or isinstance(stm, ast.While):
                if isinstance(stm.test, ast.Compare):
                    if isinstance(stm.test.left, ast.Name):
                        if stm.test.left.id in globalVars and stm.test.left.id not in localVars:
                            self.varOutsideFuncScope = True
                    
                    if isinstance(stm.test.left, ast.Subscript):
                        iterateSubscript(stm.test.left, localVars, globalVars)
                        
                    for item in stm.test.comparators:
                        if isinstance(item, ast.Name):
                            if item.id in globalVars and item.id not in localVars:
                                self.varOutsideFuncScope = True

                        if isinstance(item, ast.Subscript):
                            iterateSubscript(item, localVars, globalVars)
        
        def testFor(stm, localVars, globalVars):
            if isinstance(stm, ast.For):
                if isinstance(stm.iter, ast.Name):
                    if stm.iter.id in globalVars and stm.iter.id not in localVars:
                        self.varOutsideFuncScope = True

                if isinstance(stm.iter, ast.Call):
                    #FunctionCall's arguments e.g. print(<var>), (...).append(<var>)
                    for arg in stm.iter.args:
                        if isinstance(arg, ast.Name):
                            if arg.id in globalVars and arg.id not in localVars:
                                self.varOutsideFuncScope = True


        for node in ast.walk(root):
            #Classes are not expected in the context of MC³, this should avoid errors
            if isinstance(node, ast.ClassDef):
                return 

        globalVars = getGlobalVars(root)

        for node in ast.walk(root):
            if isinstance(node, ast.FunctionDef):
              
                localVars = getLocalVars(node, globalVars)
                
                for item in node.body:
                    for stm in ast.walk(item):
                        testFunctionCall(stm, localVars, globalVars)
                        testAssign(stm, localVars, globalVars)
                        testAugAssign(stm, localVars, globalVars)
                        testConditionals(stm, localVars, globalVars)
                        testFor(stm, localVars, globalVars)

    def checkListOverusage(self, root, numListTheshold = 0):
        """Designed as a counter for E2 - Redundant or unnecessary use of lists.
           
           Checks the whole tree if an Assign has a List as a value. The method
           counts all lists declarations and checks if their total is greater or
           equal to the assigned threshold. If no threshold is specified, the 
           method considers all that are greater or equal to 0.
            
           Rationale: if the code has too many lists and it is not "needed" for 
           the assignment, E2 might be present. The instructor will decide the
           expected threshold for each assignment.
        """
        numLists = 0
        for node in ast.walk(root):
            if isinstance(node, ast.Assign):
               if isinstance(node.value, ast.List):
                    numLists += 1
        
        if numLists > 0 and numLists >= numListTheshold:
            self.listOverusage = True
    
    def checkNonSignificantNames(self, root, varLenThreshold, funcLenThreshold, totalNamesThreshold):
        """Designed as a counter for G4 - Functions/variables with non significant 
           name.
           
           Checks the whole tree and gathers all the names for declared variables
           and functions. Then computers their length and compares them to two
           thresholds: 1) a minimum length that the variables and functions should
           have; and 2) a percentage of the total number of variables/functions that
           the number of variables/functions that do not meet 1) must surpass in
           order to consider the program with non significant names for variables
           or functions.
            
           Rationale: if the names of variables and functions are too short, there
           is a chance they are not significant. The instructor should decide, based on
           the assignment, the given thresholds required in this method.
        """
        def collectVariableNames(root):
            """Collects the names of all user declared variables in the program.
            """
            declaredVariablesNames = []
            for node in ast.walk(root):
                if isinstance(node, ast.Assign):
                    for tgt in node.targets:
                        if isinstance(tgt, ast.Name):
                            if tgt.id not in declaredVariablesNames:
                                declaredVariablesNames.append(tgt.id)
                        
                        if isinstance(tgt, ast.Tuple):
                            for item in tgt.elts:
                                if isinstance(item, ast.Name):
                                    if item.id not in declaredVariablesNames:
                                        declaredVariablesNames.append(item.id)
    
            return declaredVariablesNames
    
        def collectFunctionNames(root):
            """Collects the names of all user declared functions in the program.
            """
            declaredFunctionNames = []
            for node in ast.walk(root):
                if isinstance(node, ast.FunctionDef):
                    if node.name not in declaredFunctionNames:
                        declaredFunctionNames.append(node.name)
            
            return declaredFunctionNames
        
        def calculateNameLengthTotals(lenVarNames, lenFuncNames):
            """Calculates the length of the names of all user declared 
               variables and functions in the program.
            """
            for name in varNames:
                if len(name) not in lenVarNames:
                    lenVarNames[len(name)] = 1
                else:
                    lenVarNames[len(name)] += 1

            for name in funcNames:
                if len(name) not in lenFuncNames:
                    lenFuncNames[len(name)] = 1
                else:
                    lenFuncNames[len(name)] += 1

        def checkdeclaredVars(varNames, lenVarNames, nameThreshold, totalVarsThreshold):
            """Checks if the length of the names of all user declared 
               variables DO NOT surpass the specified thresholds.
            """
            totalVars = len(varNames)
            totalNonSignificant = 0

            for length, total in lenVarNames.items():
                if length <= nameThreshold:
                    totalNonSignificant += total

            if totalVars != 0:
                if totalNonSignificant >= totalVars*totalVarsThreshold/100:
                    self.nonSignificantNames = True

        def checkdeclaredFuncs(funcNames, lenFuncNames, nameThreshold, totalFuncsThreshold):
            """Checks if the length of the names of all user declared 
               functions DO NOT surpass the specified thresholds.
            """
            totalFuncs = len(funcNames)
            totalNonSignificant = 0

            for length, total in lenFuncNames.items():
                if length <= nameThreshold:
                    totalNonSignificant += total
                    
            if totalFuncs != 0:
                if totalNonSignificant >= totalFuncs*totalFuncsThreshold/100:
                    self.nonSignificantNames = True

        
        lenVarNames, lenFuncNames = {}, {}

        varNames = collectVariableNames(root)
        funcNames = collectFunctionNames(root)

        calculateNameLengthTotals(lenVarNames, lenFuncNames)

        checkdeclaredVars(varNames, lenVarNames, varLenThreshold, totalNamesThreshold)
        checkdeclaredFuncs(funcNames, lenFuncNames, funcLenThreshold, totalNamesThreshold)

    def checkArbitraryDeclarations(self, root):
        """Designed as a counter for G5 - Arbitrary organization of declarations.
           
           Checks the whole tree and calculates the total number of declared
           functions (N). Then, it checks if the N-first declarations are function
           definitions. Will only work with declarations made at module level
           (e.g. functions declared inside other functions will not be checked).
            
           Rationale: if there are N functions declared in the code, but those are
           not the first N declarations, it means those functions are probably in
           arbitrary places in the code.
        """
        def countFunctions(root):
            numFunc = 0
            for node in ast.iter_child_nodes(root):
                if isinstance(node, ast.FunctionDef):
                    numFunc += 1

            return numFunc
        
        numFunc = countFunctions(root)

        def checkBlockComment(node):
            isBlockComment = False

            if isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Constant):
                    if isinstance(node.value.value, str):
                        isBlockComment = True
            
            return isBlockComment

        lst = [node for node in ast.iter_child_nodes(root) if not checkBlockComment(node)]
       
        for node in lst[:numFunc]:
            if not isinstance(node, ast.FunctionDef):
                self.arbitraryDeclarations = True

    def checkNoEffectStatement(self, root):
        """Designed as a counter for H1 - Statement with no effect.
           
           Checks the whole tree for an Expression with a constant as its value.
           Examples of this are loose numbers or Boolean values, not declared to
           any variable. This method can later be incremented to check for functions
           in which its results are not returned to any variable e.g. "round(a, 2)".
            
           Rationale: numbers or Boolean values should be assigned to variables
           if they ought to have any meaning.
        """

        for node in ast.walk(root):
            if isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Constant):

                    #Ignores block comments parsed as empty string constants
                    if not isinstance(node.value.value, str):
                        self.noEffectStatement = True

    def getA4(self, root):
        '''A4 - Redefinition of built-in.'''
        self.checkBuiltInRedefinition(root)
        return self.builtinRedefinition, self.declaredVariablesAsBuiltIn, \
               self.declaredFunctionsAsBuiltin, self.declaredArgumentsAsBuiltin

    def getB6(self, root):
        '''B6 - Boolean comparison attempted with while loop.'''
        self.checkBooleanAttemptedWithWhile(root)
        return self.boolOpAttemptedWithWhile
    
    def getB8(self, root):
        '''B8 - Non utilisation of elif/else.'''
        self.checkNonUtilizationElifElse(root)
        return self.nonUtilizationElifElse
    
    def getB9(self, root):
        '''B9 - elif/else retesting already checked conditions'''
        self.checkElifRetestingCondition(root)
        return self.elifRetestingCondition
    
    def getB12(self, root):
        '''B12 - Consecutive equal if statements with distinct operations in 
           their blocks.'''
        self.checkConsecutiveIfs(root)
        return self.consecutiveEqualIfs

    def getC1(self, root):
        '''C1 - While condition tested again inside its block'''
        self.checkWhileCondInItsBody(root)
        return self.whileCondInItsBody

    def getC2(self, root):
        '''C2 - Redundant or unnecessary loop.'''
        self.checkRedundantLoop(root)
        return self.redundantLoop
    
    def getC4(self, root, constThreshold):
        '''C4 - Arbitrary number of for loop execution instead of while.'''
        self.checkForWithConstant(root, constThreshold)
        return self.forWithConstant

    def getC8(self, root):
        '''C8 - for loop having its iteration variable overwritten'''
        self.checkForOverwritten(root, [])
        return self.forVariableOverwritten
    
    def getD4(self, root):
        self.checkVarOutsideFuncScope(root)
        return self.varOutsideFuncScope

    def getE2(self, root, numListsThreshold = 0):
        '''E2 - Redundant or unnecessary use of lists.'''
        self.checkListOverusage(root, numListsThreshold)
        return self.listOverusage

    def getG4(self, root, varLenThreshold, funcLenThreshold, totalNamesThreshold):
        '''G4 - Functions/variables with non significant name.'''
        self.checkNonSignificantNames(root, varLenThreshold, 
                                      funcLenThreshold, totalNamesThreshold)
        return self.nonSignificantNames
    
    def getG5(self, root):
        '''G5 - Arbitrary organization of declarations.'''
        self.checkArbitraryDeclarations(root)
        return self.arbitraryDeclarations
    
    def getH1(self, root):
        '''H1 - Statement with no effect.'''
        self.checkNoEffectStatement(root)
        return self.noEffectStatement