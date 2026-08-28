"""
6.101 Lab:
LISP Interpreter Part 2
"""

#!/usr/bin/env python3
import sys

sys.setrecursionlimit(20_000)


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


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
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
    i = 0
    while i < len(source):
        char = source[i]
        # skip whitespace
        if char in " \n":
            i += 1
            continue
        # skip comments
        elif char == ";":
            while i < len(source) and source[i] != "\n":
                i += 1
        # add parentheses as individual tokens
        elif char in "()":
            tokens.append(char)
            i += 1
        else:
            # otherwise, read a token until next whitespace or paren
            start = i
            while i < len(source) and source[i] not in "(); \n":
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
        if index >= len(tokens):
            raise SchemeSyntaxError
        token = tokens[index]
        # starting an expression
        if token == "(":
            expr = []
            index += 1
            # open paranthesis followed by nothing
            while True:
                if index >= len(tokens):
                    raise SchemeSyntaxError  # Missing closing parenthesis
                # stops when reaches a close parenthesis
                if tokens[index] == ")":
                    return expr, index + 1
                sym, index = parse_expr(index)
                expr.append(sym)
        elif token == ")":
            # starts with close paranthesis
            raise SchemeSyntaxError
        # regular symbol, word, or number
        else:
            return number_or_symbol(token), index + 1

    parsed, next_index = parse_expr(0)
    if next_index != len(tokens):
        raise SchemeSyntaxError
    return parsed


######################
# Built-in Functions #
######################


def calc_sub(*args):
    if len(args) == 1:
        return -args[0]

    first_num, *rest_nums = args
    return first_num - scheme_builtins["+"](*rest_nums)


def calc_mul(*args):
    prod = 1
    for num in args:
        prod *= num
    return prod


def calc_div(*args):
    ans = args[0]
    for num in args[1:]:
        ans /= num
    return ans


def equal(*args):
    val = args[0]
    for item in args[1:]:
        if item != val:
            return False
    return True


def greater_than(*args):
    for i in range(len(args) - 1):
        if args[i] <= args[i + 1]:
            return False
    return True


def greater_eq(*args):
    for i in range(len(args) - 1):
        if args[i] < args[i + 1]:
            return False
    return True


def less_than(*args):
    for i in range(len(args) - 1):
        if args[i] >= args[i + 1]:
            return False
    return True


def less_eq(*args):
    for i in range(len(args) - 1):
        if args[i] > args[i + 1]:
            return False
    return True


def func_not(*exp):
    if len(exp) != 1:
        raise SchemeEvaluationError
    return not evaluate(exp[0])


def car(*args):
    if len(args) != 1:
        raise SchemeEvaluationError
    pair = args[0]
    if not isinstance(pair, Pair):
        raise SchemeEvaluationError
    return pair.car


def cdr(*args):
    if len(args) != 1:
        raise SchemeEvaluationError
    pair = args[0]
    if not isinstance(pair, Pair):
        raise SchemeEvaluationError
    return pair.cdr


def create_list(*args):
    result = None  # empty list at first
    for item in reversed(args):
        result = Pair(item, result)
    return result


def is_list(*args):
    if len(args) != 1:
        raise SchemeEvaluationError
    lst = args[0]
    if lst is None:
        return True
    while isinstance(lst, Pair):
        lst = lst.cdr
    # is linked list if it ends in None
    if lst is None:
        return True
    return False


def length(*args):
    if len(args) != 1:
        raise SchemeEvaluationError
    lst = args[0]
    count = 0
    while lst is not None:
        if not isinstance(lst, Pair):
            raise SchemeEvaluationError
        count += 1
        lst = lst.cdr
    return count


def list_ref(*args):
    if len(args) != 2:
        raise SchemeEvaluationError
    item = args[0]  # the pair
    index = args[1]
    if not isinstance(index, int):
        raise SchemeEvaluationError
    for _ in range(index):
        if not isinstance(item, Pair):
            raise SchemeEvaluationError
        item = item.cdr
    if isinstance(item, Pair):
        return item.car
    raise SchemeEvaluationError


def append(*args):
    def make_shallow(lis):
        if not is_list(lis):
            raise SchemeEvaluationError
        if lis is None:
            return None
        return Pair(lis.car, make_shallow(lis.cdr))

    result = None
    for lst in reversed(args):
        copy = make_shallow(lst)
        if copy is None:
            continue
        # gets last pair item in list
        tail = copy
        while tail.cdr is not None:
            tail = tail.cdr
        tail.cdr = result
        result = copy
    return result


scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": calc_mul,
    "/": calc_div,
    "#t": True,
    "#f": False,
    "equal?": equal,
    ">": greater_than,
    "<": less_than,
    ">=": greater_eq,
    "<=": less_eq,
    "not": func_not,
    "car": car,
    "cdr": cdr,
    "list": create_list,
    "list?": is_list,
    "length": length,
    "list-ref": list_ref,
    "append": append,
}

###########
# Classes #
###########


class Frame:
    """
    Represents a frame for a function call or evaluating expressions,
    holds variables, and potentially has a parent
    """

    def __init__(self, parent=None, vars=None):
        if vars is None:
            vars = {}
        self.parent = parent
        self.vars = vars

    def __setitem__(self, var, val):
        self.vars[var] = val

    def __getitem__(self, var):
        if var in self.vars:
            return self.vars[var]
        if self.parent:
            return self.parent[var]  # recursive call
        raise SchemeNameError

    def delete_var(self, var):
        if var in self.vars:
            val = self.vars[var]
            del self.vars[var]
            return val
        raise SchemeNameError

    def get_enclosing(self, var):
        frame = self
        while frame.parent is not None:
            if var in frame.vars:
                return frame
            frame = frame.parent
        if var in frame.vars:
            return frame
        raise SchemeNameError


class Function:
    """
    Represents a user-defined function, has a body expression, parameters,
    and the frame it was defined in.
    """

    def __init__(self, body, parameters, frame):
        """
        Given body, the code representing the body of the function
        (a single expression representing the return value)
        a list of parameters(default value is none), and
        the frame where the function was defined
        """
        self.parameters = parameters
        self.body = body
        self.frame = frame

    def bind_parameters(self, bind_frame, arguments):
        """
        Given a frame to call the function, bind the parameters of
        the function to the arguments passed in(list).
        """
        if len(arguments) != len(self.parameters):
            raise SchemeEvaluationError
        for p, a in zip(self.parameters, arguments):
            bind_frame[p] = a


class Pair:
    """
    Represents a con cell with car and cdr values.
    """

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr


##############
# Evaluation #
##############
built_in_frame = Frame(None, scheme_builtins)


def make_initial_frame():
    """
    takes no arguments and returns a single new frame representing the initial
    frame (i.e., an empty frame that has the builtins as its parent).
    """
    return Frame(built_in_frame)


# Creating function dictionary
def let(tree, frame):
    """
    setting local functions
    """
    new_frame = Frame(frame)
    for var_exp in tree[1]:
        var = var_exp[0]
        val = var_exp[1]
        val = evaluate(val, frame)
        new_frame[var] = val
    return evaluate(tree[2], new_frame)


def set_bang(tree, frame):
    expr = evaluate(tree[2], frame)
    enc_fr = frame.get_enclosing(tree[1])
    enc_fr[tree[1]] = expr
    return expr


def begin(tree, frame):
    if len(tree) < 2:
        raise SchemeEvaluationError
    for exp in tree[1:-1]:
        evaluate(exp, frame)
    return evaluate(tree[-1], frame)


def delete(tree, frame):
    return frame.delete_var(tree[1])


def cons(tree, frame):
    if len(tree[1:]) != 2:
        raise SchemeEvaluationError
    return Pair(evaluate(tree[1], frame), evaluate(tree[2], frame))


def and_func(tree, frame):
    for esp in tree[1:]:
        # if one of expressions is false, return f
        if evaluate(esp, frame) == False:
            return False
    return True


def or_func(tree, frame):
    for esp in tree[1:]:
        # if one of expressions is true, return t
        if evaluate(esp, frame) == True:
            return True
    return False


def if_func(tree, frame):
    # not enough arguments
    if len(tree) != 4:
        raise SchemeEvaluationError
    # if evaluating predicate returns true, return true exp
    if evaluate(tree[1], frame):
        return evaluate(tree[2], frame)
    return evaluate(tree[3], frame)


def define_func(tree, frame):
    var = tree[1]
    # simple function notation
    if isinstance(var, list):
        name = var[0]
        function = Function(tree[2], var[1:], frame)
        frame[name] = function
        return function
    exp = evaluate(tree[2], frame)
    frame[var] = exp
    return exp


def lambda_func(tree, frame):
    return Function(tree[2], tree[1], frame)


eval_funcs = {
    "let": let,
    "begin": begin,
    "set!": set_bang,
    "del": delete,
    "cons": cons,
    "and": and_func,
    "or": or_func,
    "if": if_func,
    "define": define_func,
    "lambda": lambda_func,
}


def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if frame is None:
        frame = make_initial_frame()
    if isinstance(tree, (int, float)):
        return tree
    if isinstance(tree, str):
        return frame[tree]
    if isinstance(tree, list):
        # empty list
        if not tree:
            return None
        eval_f = tree[0]
        if isinstance(eval_f, str) and eval_f in eval_funcs:
            return eval_funcs[eval_f](tree, frame)
        func = evaluate(tree[0], frame)
        # calling user-created function
        if isinstance(func, Function):
            # get arguments and evaluate each one
            args = tree[1:]
            evaluated_args = [evaluate(a, frame) for a in args]
            # create a new frame where the parent is the function's defined frame
            new_frame = Frame(func.frame)
            # bind the arguments to function parameters
            func.bind_parameters(new_frame, evaluated_args)
            result = evaluate(func.body, new_frame)
            return result
        if not callable(func):
            raise SchemeEvaluationError
        # built-in functions
        arguments = []
        for item in tree[1:]:
            arguments.append(evaluate(item, frame))
        return func(*arguments)
    else:
        raise SchemeNameError


def evaluate_file(file, frame=None):
    """
    Given file: a string containing the name of a file to be evaluated)
    and frame: an optional argument (the frame in which to evaluate the expression)
    Returns the result of evaluating the expression contained in the file
    """
    if frame is None:
        frame = make_initial_frame()
    with open(file) as f:
        string = f.read()
    expr = parse(tokenize(string))
    return evaluate(expr, frame)


if __name__ == "__main__":
    import os

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl

    new_frame = None
    if len(sys.argv) != 1:
        new_frame = make_initial_frame()
        for file in sys.argv[1:]:
            evaluate_file(file, new_frame)
    schemerepl.SchemeREPL(
        sys.modules[__name__], use_frames=True, verbose=False, repl_frame=new_frame
    ).cmdloop()
    # print(tokenize("(+ x 2))"))
    # print(parse(['(', '+', 'x', '2', ')', ')']))
    # lst = create_list(5, 4)
    # print(list_ref(lst, 2))
