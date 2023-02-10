class Node:
    def toString(self):
        raise Exception('Unimplemented method')

    def interpret(self):
        raise Exception('Unimplemented method')

    def children(self, dsl):
        raise Exception('Unimplemented method')

    def complete(self):
        raise Exception('Unimplemented method')

class NonTerminalNode(Node):
    def toString(self):
        return "@"

    def complete(self):
        return False

class Not(Node):
    def __init__(self, left=NonTerminalNode()):
        self.left = left

    def toString(self):
        return 'not (' + self.left.toString() + ')'

    def interpret(self, env):
        return not (self.left.interpret(env))

    def children(self, dsl):
        pass

    def complete(self):
        return self.left.complete()

class And(Node):
    def __init__(self, left=NonTerminalNode(), right=NonTerminalNode()):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " and " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) and self.right.interpret(env)

    def children(self, dsl):
        pass

    def complete(self):
        return self.left.complete() and self.right.complete()

class Lt(Node):
    def __init__(self, left=NonTerminalNode(), right=NonTerminalNode()):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " < " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) < self.right.interpret(env)

    def children(self, dsl):
        pass

    def complete(self):
        return self.left.complete() and self.right.complete()

class Ite(Node):
    def __init__(self, condition=NonTerminalNode(), true_case=NonTerminalNode(), false_case=NonTerminalNode()):
        self.condition = condition
        self.true_case = true_case
        self.false_case = false_case

    def toString(self):
        return "(if" + self.condition.toString() + " then " + self.true_case.toString() + " else " + self.false_case.toString() + ")"

    def interpret(self, env):
        if self.condition.interpret(env):
            return self.true_case.interpret(env)
        else:
            return self.false_case.interpret(env)

    def children(self, dsl):
        if not self.condition.complete():
            pass

    def complete(self):
        return self.condition.complete() and self.true_case.complete() and self.false_case.complete()

class Num(Node):
    def __init__(self, value):
        self.value = value

    def toString(self):
        return str(self.value)

    def interpret(self, env):
        return self.value
    
    def complete(self):
        return True

class Var(Node):
    def __init__(self, name):
        self.name = name

    def toString(self):
        return self.name

    def interpret(self, env):
        return env[self.name]
    
    def complete(self):
        return True

class Plus(Node):
    def __init__(self, left=NonTerminalNode(), right=NonTerminalNode()):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " + " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) + self.right.interpret(env)

    def children(self, dsl):
        if not self.left.complete():
            for symbol in dsl:
                if type(symbol) in [Var, Num, Plus, Times]:
                    self.left = symbol
                    yield self
        if not self.right.complete():
            for symbol in dsl:
                self.right = symbol
                yield self
        return [self]

    def complete(self):
        return self.left.complete() and self.right.complete()

class Times(Node):
    def __init__(self, left=NonTerminalNode(), right=NonTerminalNode()):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " * " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) * self.right.interpret(env)
    
    def children(self, dsl):
        pass

    def complete(self):
        return self.left.complete() and self.right.complete()

class TopDownSearch():
    # Top-down representative breadth-first search
    def children(self, program, dsl):
        # returns a list of programs (children of the given node)
        if program.complete():
            return [program]
        else:
            return program.children(dsl)

    def evaluate(self, program, input_output):
        for case in input_output:
            if case["out"] != program.interpret(case):
                return False
        return True

    def synthesize(self, bound, operations, integer_values, variables, input_output):
        dsl = list([operation() for operation in operations]) + \
            list([Num(integer_value) for integer_value in integer_values]) + \
            list([Var(variable) for variable in variables])
        plist = list([NonTerminalNode()])
        production = 0
        while len(plist) > 0 and production < bound:
            p = plist.pop(0)
            children = self.children(p, dsl)
            for p_prime in children:
                if p_prime.complete() and self.evaluate(p, input_output):
                    print("Successfully found a program: {}".format(p_prime))
                    return p_prime
                if not p_prime.complete():
                    plist.append(p_prime)
            production += 1
        print("Failed to find a satisfying program")
        return None      
        
        


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
