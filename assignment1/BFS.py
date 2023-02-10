import time

def report(synthesizer):
    def inner(*args, **kwargs):
        '''
        Running time
        # of generated programs
        # of evaluated programs
        '''
        start_time = time.time()
        program = synthesizer(*args, **kwargs)
        runtime = time.time() - start_time
        if program is None:
            print("Failed to find a satisfying program")
        else:
            print("Successfully found a satisfying program in {}: \n{}".format(runtime, program))
        
    return inner

class Node:
    def toString(self):
        raise Exception('Unimplemented method')

    def interpret(self):
        raise Exception('Unimplemented method')

    def children(self, dsl):
        raise Exception('Unimplemented method')

    def complete(self):
        raise Exception('Unimplemented method')

    def size(self):
        raise Exception('Unimplemented method')

class NonTerminalNode(Node):
    def toString(self):
        return "@"

    def complete(self):
        return False

    def size(self):
        # Here I use the production rule to stop the program, so the size of non-terminal node is 0
        return 0

class Not(Node):
    def __init__(self, left=NonTerminalNode()):
        self.left = left

    def toString(self):
        return 'not (' + self.left.toString() + ')'

    def interpret(self, env):
        return not (self.left.interpret(env))

    def children(self, dsl):
        if type(self.left) == NonTerminalNode:
            yield Not(Lt())
        else:
            if not self.left.complete():
                for child in self.left.children(dsl):
                    yield Not(child)

    def complete(self):
        return self.left.complete()

    def size(self):
        return self.left.size() + 1

class And(Node):
    def __init__(self, left=NonTerminalNode(), right=NonTerminalNode()):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " and " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) and self.right.interpret(env)

    def children(self, dsl):
        if type(self.left) == NonTerminalNode:
            yield And(Lt(), self.right)
        elif type(self.right) == NonTerminalNode:
            yield And(self.left, Lt())
        else:
            if not self.left.complete():
                for child in self.left.children(dsl):
                    yield And(child, self.right)
            elif not self.right.complete():
                for child in self.right.children(dsl):
                    yield And(self.left, child)

    def complete(self):
        return self.left.complete() and self.right.complete()

    def size(self):
        return self.left.size() + self.right.size() + 1

class Lt(Node):
    def __init__(self, left=NonTerminalNode(), right=NonTerminalNode()):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " < " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) < self.right.interpret(env)

    def children(self, dsl):
        constraint_dsl = list([symbol for symbol in dsl if type(symbol) in [Var, Num, Times, Plus]])
        if type(self.left) == NonTerminalNode:
            for symbol in constraint_dsl:
                yield Lt(symbol, self.right)
        elif type(self.right) == NonTerminalNode:
            for symbol in constraint_dsl:
                yield Lt(self.left, symbol)
        else:
            if not self.left.complete():
                for child in self.left.children(dsl):
                    yield Lt(child, self.right)
            elif not self.right.complete():
                for child in self.right.children(dsl):
                    yield Lt(self.left, child)

    def complete(self):
        return self.left.complete() and self.right.complete()

    def size(self):
        return self.left.size() + self.right.size() + 1

class Ite(Node):
    def __init__(self, condition=NonTerminalNode(), true_case=NonTerminalNode(), false_case=NonTerminalNode()):
        self.condition = condition
        self.true_case = true_case
        self.false_case = false_case

    def toString(self):
        return "(if " + self.condition.toString() + " then " + self.true_case.toString() + " else " + self.false_case.toString() + ")"

    def interpret(self, env):
        if self.condition.interpret(env):
            return self.true_case.interpret(env)
        else:
            return self.false_case.interpret(env)

    def children(self, dsl):
        constraint_dsl = list([symbol for symbol in dsl if type(symbol) in [And, Not, Lt]])
        if type(self.condition) == NonTerminalNode:
            for symbol in constraint_dsl:
                yield Ite(symbol, self.true_case, self.false_case)
        elif type(self.true_case) == NonTerminalNode:
            for symbol in dsl:
                yield Ite(self.condition, symbol, self.false_case)
        elif type(self.false_case) == NonTerminalNode:
            for symbol in dsl:
                yield Ite(self.condition, self.true_case, symbol) 
        else:
            if not self.condition.complete():
                for child in self.condition.children(dsl):
                    yield Ite(child, self.true_case, self.false_case)
            elif not self.true_case.complete():
                for child in self.true_case.children(dsl):
                    yield Ite(self.condition, child, self.false_case)
            elif not self.false_case.complete():
                for child in self.false_case.children(dsl):
                    yield Ite(self.condition, self.true_case, child)
        
    def complete(self):
        return self.condition.complete() and self.true_case.complete() and self.false_case.complete()

    def size(self):
        return self.condition.size() + self.true_case.size() + self.false_case.size() + 1

class Num(Node):
    def __init__(self, value):
        self.value = value

    def toString(self):
        return str(self.value)

    def interpret(self, env):
        return self.value
    
    def complete(self):
        return True

    def size(self):
        return 1

class Var(Node):
    def __init__(self, name):
        self.name = name

    def toString(self):
        return self.name

    def interpret(self, env):
        return env[self.name]
    
    def complete(self):
        return True

    def size(self):
        return 1

class Plus(Node):
    def __init__(self, left=NonTerminalNode(), right=NonTerminalNode()):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " + " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) + self.right.interpret(env)

    def children(self, dsl):
        constraint_dsl = list([symbol for symbol in dsl if type(symbol) in [Var, Num, Times, Plus]])
        if type(self.left) == NonTerminalNode:
            for symbol in constraint_dsl:
                yield Plus(symbol, self.right)
        elif type(self.right) == NonTerminalNode:
            for symbol in constraint_dsl:
                yield Plus(self.left, symbol)
        else:
            if not self.left.complete():
                for child in self.left.children(dsl):
                    yield Plus(child, self.right)
            elif not self.right.complete():
                for child in self.right.children(dsl):
                    yield Plus(self.left, child)

    def complete(self):
        return self.left.complete() and self.right.complete()

    def size(self):
        return self.left.size() + self.right.size() + 1

class Times(Node):
    def __init__(self, left=NonTerminalNode(), right=NonTerminalNode()):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " * " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) * self.right.interpret(env)
    
    def children(self, dsl):
        constraint_dsl = list([symbol for symbol in dsl if type(symbol) in [Var, Num, Times, Plus]])
        if type(self.left) == NonTerminalNode:
            for symbol in constraint_dsl:
                yield Times(symbol, self.right)
        elif type(self.right) == NonTerminalNode:
            for symbol in constraint_dsl:
                yield Times(self.left, symbol)
        else:
            if not self.left.complete():
                for child in self.left.children(dsl):
                    yield Times(child, self.right)
            elif not self.right.complete():
                for child in self.right.children(dsl):
                    yield Times(self.left, child)

    def complete(self):
        return self.left.complete() and self.right.complete()

    def size(self):
        return self.left.size() + self.right.size() + 1

class TopDownSearch():
    # Top-down representative breadth-first search
    def children(self, program, dsl):
        # returns a list of programs
        if program.complete():
            return [program]
        else:
            return program.children(dsl)

    def evaluate(self, program, input_output):
        for case in input_output:
            if case["out"] != program.interpret(case):
                return False
        return True

    @report
    def synthesize(self, bound, operations, integer_values, variables, input_output):
        dsl =  list([Num(integer_value) for integer_value in integer_values]) + \
            list([Var(variable) for variable in variables]) + \
            list([operation() for operation in operations])
        plist = list(dsl)
        while len(plist) > 0 and plist[0].size() <= bound:
        # all(map(lambda x: x.size() < bound, plist)):
            p = plist.pop(0)
            children = self.children(p, dsl)
            for p_prime in children:
                if p_prime.complete() and self.evaluate(p_prime, input_output):
                    return p_prime
                if not p_prime.complete():
                    plist.append(p_prime)
        return None      
        
print("Top-Down Search")
synthesizer = TopDownSearch()
# synthesizer.synthesize(10, [Lt, Ite], [1, 2], ['x', 'y'], [{'x':5, 'y': 10, 'out':5}, {'x':10, 'y': 5, 'out':5}, {'x':4, 'y': 3, 'out':3}])
# synthesizer.synthesize(12, [And, Plus, Times, Lt, Ite, Not], [10], ['x', 'y'], [{'x':5, 'y': 10, 'out':5}, {'x':10, 'y': 5, 'out':5}, {'x':4, 'y': 3, 'out':4}, {'x':3, 'y': 4, 'out':4}])
# synthesizer.synthesize(11, [And, Plus, Times, Lt, Ite, Not], [-1, 5], ['x', 'y'], [{'x':10, 'y':7, 'out':17},
# {'x':4, 'y':7, 'out':-7},
# {'x':10, 'y':3, 'out':13},
# {'x':1, 'y':-7, 'out':-6},
# {'x':1, 'y':8, 'out':-8}])

# S -> 1 | 2 | x | y | S < S | If S then S else S
synthesizer.synthesize(10, [Lt, Ite], [1, 2], ['x', 'y'], [{'x':5, 'y': 10, 'out':5}, {'x':10, 'y': 5, 'out':5}, {'x':4, 'y': 3, 'out':3}])
# S -> 10 | x | y | S + S | S * S | S < S | If S then S else S
synthesizer.synthesize(12, [And, Times, Lt, Ite], [10], ['x', 'y'], [{'x':5, 'y': 10, 'out':5}, {'x':10, 'y': 5, 'out':5}, {'x':4, 'y': 3, 'out':4}, {'x':3, 'y': 4, 'out':4}])
# S -> -1 | x | y | S + S | S * S | S < S | If S then S else S
synthesizer.synthesize(11, [Plus, Times, Lt, Ite], [-1], ['x', 'y'], [{'x':10, 'y':7, 'out':17},
{'x':4, 'y':7, 'out':-7},
{'x':10, 'y':3, 'out':13},
{'x':1, 'y':-7, 'out':-6},
{'x':1, 'y':8, 'out':-8}])
