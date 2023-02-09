from itertools import product

class Node:
    def toString(self):
        raise Exception('Unimplemented method')

    def interpret(self):
        raise Exception('Unimplemented method')

    def grow(plist, size):
        raise Exception('Unimplemented method')

    def size(self):
        raise Exception('Unimplemented method')

class Not(Node):
    def __init__(self, left):
        self.left = left

    def toString(self):
        return 'not (' + self.left.toString() + ')'

    def interpret(self, env):
        return not (self.left.interpret(env))

    def grow(plist, size):
        pass

    def size(self):
        return self.left.size() + 1

class And(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " and " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) and self.right.interpret(env)

    def grow(plist, size):
        pass

    def size(self):
        return self.left.size() + self.right.size() + 1

class Lt(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " < " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) < self.right.interpret(env)

    def grow(plist, size):
        new_plist = []
        for (p1, p2) in product(plist, plist):
            if type(p1) in [Var, Num, Times, Plus] and type(p2) in [Var, Num, Times, Plus] and Lt(p1, p2).size() == size:
                new_plist.append(Lt(p1, p2))
        return new_plist
    
    def size(self):
        return self.left.size() + self.right.size() + 1

class Ite(Node):
    def __init__(self, condition, true_case, false_case):
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

    def grow(plist, size):
        new_plist = []
        for (p1, p2, p3) in product(plist, plist, plist):
            if type(p1) in [And, Not, Lt] and Ite(p1, p2, p3).size() == size:
                new_plist.append(Ite(p1, p2, p3))
        return new_plist

    def size(self):
        return self.condition.size() + self.true_case.size() + self.false_case.size() + 1

class Num(Node):
    def __init__(self, value):
        self.value = value

    def toString(self):
        return str(self.value)

    def interpret(self, env):
        return self.value

    def size(self):
        return 1

class Var(Node):
    def __init__(self, name):
        self.name = name

    def toString(self):
        return self.name

    def interpret(self, env):
        return env[self.name]
    
    def size(self):
        return 1
    
class Plus(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " + " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) + self.right.interpret(env)

    def grow(plist, size):
        new_plist = []
        for (p1, p2) in product(plist, plist):
            if type(p1) in [Var, Num, Times, Plus] and type(p2) in [Var, Num, Times, Plus] and Plus(p1, p2).size() == size:
                new_plist.append(Plus(p1, p2))
        return new_plist

    def size(self):
        return self.left.size() + self.right.size() + 1

class Times(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toString(self):
        return "(" + self.left.toString() + " * " + self.right.toString() + ")"

    def interpret(self, env):
        return self.left.interpret(env) * self.right.interpret(env)
    
    def grow(plist, size):
        pass

    def size(self):
        return self.left.size() + self.right.size() + 1

class BottomUpSearch():
    # Enumerative bottom-up search
    def grow(self, plist, operations, input_output, output, size):
        new_plist = []
        for operation in operations:
            new_plist += operation.grow(plist, size)
        for p in new_plist:
            # if p has no observational equivalent programs, add to plist
            observation_list = []
            for case in input_output:
                out = p.interpret(case)
                observation = dict(case)
                observation["out"] = out
                observation_list.append(observation)
            observation_list = str(observation_list)
            if observation_list not in output:
                plist.append(p)
                output.add(observation_list)
        return plist

    
    def evaluate(self, program, input_output):
        for case in input_output:
            if case["out"] != program.interpret(case):
                return False
        return True

    def synthesize(self, bound, operations, integer_values, variables, input_output):
        num = list([Num(i) for i in integer_values])
        var = list([Var(i) for i in variables])
        plist = num + var
        evals = 0
        output = set()
        for i in range(1, bound):
            plist = self.grow(plist, operations, input_output, output, i)
            for j in range(evals, len(plist)):
                evals += 1
                # if satisfies, return
                if self.evaluate(plist[j], input_output):
                    print("Successfully found a program: {}".format(plist[j].toString()))
                    return plist[j]

        print("Failed to find a satisfying program")
        return None


synthesizer = BottomUpSearch()
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
