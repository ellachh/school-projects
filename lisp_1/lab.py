"""
6.101 Lab:
LISP Interpreter Part 1
"""

#!/usr/bin/env python3

# import doctest # optional import
# import typing  # optional import
# import pprint  # optional import

import sys

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    tokens = []
    i=0
    while i < len(source):
        char = source[i]
        # skip whitespace
        if char in ' \n':
            i += 1
            continue
        # skip comments
        elif char == ';':
            while i < len(source) and source[i] != '\n':
                i += 1
        # add parentheses as individual tokens
        elif char in '()':
            tokens.append(char)
            i += 1
        else:
            # otherwise, read a token until next whitespace or paren
            start = i
            while i < len(source) and source[i] not in '(); \n':
                i += 1
            tokens.append(source[start:i])
    return tokens

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    def parse_expr(index):
        token = tokens[index]
        #starting an expression
        if token == '(':
            expr = []
            index += 1
            while tokens[index] != ')':
                sym, index = parse_expr(index)
                expr.append(sym)
            return expr, index + 1
        #regular symbol, word, or number, or ')'
        else:
            return number_or_symbol(token), index + 1
    parsed, _ = parse_expr(0)
    return parsed

######################
# Built-in Functions #
######################

def calc_sub(*args):
    if len(args) == 1:
        return -args[0]

    first_num, *rest_nums = args
    return first_num - scheme_builtins['+'](*rest_nums)

def calc_mul(*args):
    prod = 1
    for num in args:
        prod*=num
    return prod

def calc_div(*args):
    ans = args[0]
    for num in args[1:]:
        ans/=num
    return ans

scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": calc_mul,
    "/": calc_div
}

###########
# Classes #
###########

class Frame():
    """
    Represents a frame for a function call or evaluating expressions, 
    holds variables, and potentially has a parent
    """
    def __init__(self, parent = None,vars = None):
        if vars is None:
            vars = {}
        self.parent = parent
        self.vars = vars
    def __setitem__(self,var,val):
        self.vars[var] = val
    def __getitem__(self,var):
        if var in self.vars:
            return self.vars[var]
        if self.parent:
            return self.parent[var]  # recursive call
        raise SchemeNameError

class Function():
    """
    Represents a user-defined function, has a body expression, parameters,
    and the frame it was defined in.
    """
    def __init__(self,body,parameters,frame):
        """
        Given body, the code representing the body of the function 
        (a single expression representing the return value)
        a list of parameters(default value is none), and
        the frame where the function was defined
        """
        self.parameters = parameters
        self.body = body
        self.frame = frame
    def bind_parameters(self,bind_frame,arguments):
        """
        Given a frame to call the function, bind the parameters of
        the function to the arguments passed in(list).
        """
        if len(arguments)!=len(self.parameters):
            raise SchemeEvaluationError
        for p,a in zip(self.parameters,arguments):
            bind_frame[p] = a

##############
# Evaluation #
##############
built_in_frame = Frame(None,scheme_builtins)

def make_initial_frame():
    """
    takes no arguments and returns a single new frame representing the initial
    frame (i.e., an empty frame that has the builtins as its parent).
    """
    return Frame(built_in_frame)

def evaluate(tree, frame = None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if frame is None:
        frame = make_initial_frame()
    if isinstance(tree,(int,float)):
        return tree
    if isinstance(tree, str):
        return frame[tree]
    if isinstance(tree,list):
        #defining an expression
        if tree[0]=='define':
            var = tree[1]
            #simple function notation
            if isinstance(var,list):
                name = var[0]
                function = Function(tree[2],var[1:],frame)
                frame[name] = function
                return function
            exp = evaluate(tree[2],frame)
            frame[var] = exp
            return exp
        #user-created function
        if tree[0]=='lambda':
            return Function(tree[2],tree[1],frame)
        func = evaluate(tree[0],frame)
        #calling user-created function
        if isinstance(func,Function):
            #get arguments and evaluate each one
            args = tree[1:]
            evaluated_args = [evaluate(a,frame) for a in args]
            #create a new frame where the parent is the function's defined frame
            new_frame = Frame(func.frame)
            #bind the arguments to function parameters
            func.bind_parameters(new_frame,evaluated_args)
            result = evaluate(func.body, new_frame)
            return result
        if not callable(func):
            raise SchemeEvaluationError
        #built-in functions
        arguments = []
        for item in tree[1:]:
            arguments.append(evaluate(item,frame))
        return func(*arguments)
    else:
        raise SchemeNameError

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    import os
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl
    schemerepl.SchemeREPL(sys.modules[__name__], use_frames=True, verbose=False).cmdloop()

    # print(tokenize("(cat (dog (tomato)))"))
    # string = """
    # ;add the numbers 2 and 3
    # (+ ; this expression
    # 2     ; spans multiple
    # 3  ; lines

    # )
    # """
    # print(tokenize(string))
    # print(parse(['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')']))
    # print(parse(['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')']))
    # print(tokenize(('+ 2 (- 3 4))')))
    # print(parse(['+', '2', '(', '-', '3', '4', ')', ')']))
    # print(calc_mul(2,3,4))
    # print(calc_div(10,2,5))
    # print(parse(tokenize("(define y 8)")))
    # f1 = Frame(built_in_frame)
    # f1['x']=3
    # print(evaluate(['define', 'y', 8],f1))
    # print(f1['y'])
    # print(parse(tokenize("(define x 7)")))
