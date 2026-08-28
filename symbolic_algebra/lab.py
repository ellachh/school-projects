"""
6.101 Lab:
Symbolic Algebra
"""

# import doctest # optional import
# import typing # optional import
# import pprint # optional import
# import string # optional import
# import abc # optional import

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Expr:
    """
    Superclass representing algebraic expressions.
    """
    def __add__(self,other):
        return Add(self,other)
    def __radd__(self,other):
        return Add(other,self)
    def __sub__(self,other):
        return Sub(self,other)
    def __rsub__(self,other):
        return Sub(other,self)
    def __mul__(self,other):
        return Mul(self,other)
    def __rmul__(self,other):
        return Mul(other,self)
    def __truediv__(self,other):
        return Div(self,other)
    def __rtruediv__(self,other):
        return Div(other,self)

class Var(Expr):
    """
    Represents variables such as x, y, z in algebra.
    """
    precedence = 3
    def __init__(self, name):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = name
    def __str__(self):
        return self.name
    def evaluate(self,mapping):
        """
        Maps variable to its assigned number in mapping. If not in mapping,
        Raise SymbolicEvaluationError
        """
        try:
            return mapping[self.name]
        except:
            raise SymbolicEvaluationError
    def __repr__(self):
        return f"Var('{self.name}')"
    def deriv(self, var):
        """
        Returns derivative of a variable. Derivative of itself is 1, 
        partial derivative of another variable is 0.
        """
        if var!=self.name:
            return Num(0)
        return Num(1)
    def simplify(self):
        """
        Returns simplified variable, which is just itself
        """
        return self

class Num(Expr):
    """
    Represents numbers in algebra
    """
    precedence = 3
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n
    def evaluate(self,_):
        return self.n
    def __str__(self):
        return str(self.n)
    def __repr__(self):
        return f"Num({self.n})"
    def deriv(self, _):
        """
        Returns derivative of a number. Always 0.
        """
        return Num(0)
    def simplify(self):
        """
        Returns simplified number, which is just itself.
        """
        return self

class BinOp(Expr):
    operator = '?' #temporary, will override
    def __init__(self, left, right):
        """
        Initializes left and right operands
        """
        self.left = self.convert(left)
        self.right = self.convert(right)

    def convert(self, operand):
        """
        Converts strings and ints/floats to Vars and Nums, respectively.
        """
        if isinstance(operand, Expr):
            return operand
        elif isinstance(operand, (int, float)):
            return Num(operand)
        elif isinstance(operand, str):
            return Var(operand)
        else:
            raise TypeError

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.left)}, {repr(self.right)})"

    def __str__(self):
        l_str = str(self.left)
        r_str = str(self.right)
        #if lower precedence, wrap in parathesis
        if self.left.precedence < self.precedence:
            l_str = f"({l_str})"
        if self.right.precedence< self.precedence:
            r_str = f"({r_str})"
        #if special case(sub or div) wrap right side in paranthesis if
        #same precedence
        if self.special and self.right.precedence==self.precedence:
            r_str = f"({r_str})"
        return l_str + ' ' + self.operator + ' ' + r_str

    def evaluate(self,mapping):
        """
        Evaluate the right and left sides of an Binary Operation.
        """
        try:
            left_var = self.left.evaluate(mapping)
            right_var = self.right.evaluate(mapping)
            return self.operate(left_var,right_var)
        except:
            raise SymbolicEvaluationError


class Add(BinOp):
    """
    Represents addition of 2 expressions
    """
    operator = '+'
    precedence = 1
    special = False
    def operate(self,left,right):
        return left + right
    def deriv(self,var):
        return self.left.deriv(var) + self.right.deriv(var)
    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        #adding 0 to another expression
        if isinstance(left,Num) and left.n==0:
            return right
        if isinstance(right,Num) and right.n==0:
            return left
        #adding 2 numbers together
        if isinstance(left,Num) and isinstance(right,Num):
            return Num(left.n+right.n)
        return left + right

class Sub(BinOp):
    operator = '-'
    precedence = 1
    special = True
    def operate(self,left,right):
        return left - right
    def deriv(self,var):
        return self.left.deriv(var) - self.right.deriv(var)
    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        #subtracting 0 from an expression
        if isinstance(right,Num) and right.n==0:
            return left
        #subtracting 2 numbers
        if isinstance(left,Num) and isinstance(right,Num):
            return Num(left.n-right.n)
        return left - right

class Div(BinOp):
    operator = '/'
    precedence = 2
    special = True
    def operate(self,left,right):
        return left / right
    def deriv(self,var):
        num = self.right*self.left.deriv(var) - self.left*self.right.deriv(var)
        return num/(self.right*self.right)
    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        #Dividing 0 by an expression
        if isinstance(left,Num) and left.n==0:
            return left
        #dividing an expression by 1
        if isinstance(right,Num) and right.n==1:
            return left
        #dividing 2 numbers
        if isinstance(left,Num) and isinstance(right,Num):
            return Num(left.n/right.n)
        return left / right

class Mul(BinOp):
    operator = '*'
    precedence = 2
    special = False
    def operate(self,left,right):
        return left * right
    def deriv(self,var):
        return self.left*self.right.deriv(var) + self.right*self.left.deriv(var)
    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        #Multiplying by 0 or 1
        if isinstance(left,Num):
            if left.n==1:
                return right
            if left.n==0:
                return Num(0)
        if isinstance(right,Num):
            if right.n==1:
                return left
            if right.n==0:
                return Num(0)
        #multiplying 2 numbers
        if isinstance(left,Num) and isinstance(right,Num):
            return Num(left.n*right.n)
        return left * right

def make_expression(express):
    """
    takes a single string as input. This string should contain either:
    a single variable name,
    a single number, or
    a fully parenthesized expression of the form (E1 op E2)
    Returns an expression.
    """
    tokens = tokenize(express)
    return parse(tokens)

def tokenize(string):
    """
    Given a string representing expression, return a list of meaningful tokens
    (parentheses, variable names, numbers, or operands).
    """
    tokens = []
    i=0
    while i <len(string):
        char = string[i]
        if char == ' ':
            i+=1
            continue
        elif char in '()+*/':
            i+=1
            tokens.append(char)
        #checks for subtraction/negative or numbers
        elif char == '-' or char.isdigit():
            start = i
            while i < len(string) and (string[i]!=' ' and string[i]!=')'):
                i += 1
            tokens.append(string[start:i])
        #checks for variables
        elif char.isalpha():
            tokens.append(char)
            i += 1
    return tokens

def parse(tokens):
    """
    Given a list like the output of tokenize, 
    convert it into an appropriate instance of Expr
    """
    def parse_expression(index):
        token = tokens[index]
        #base case: is a number or variable
        #if its a number
        try:
            value = float(token)
            if value.is_integer():
                value = int(value)
            return (Num(value), index + 1)
        except ValueError:
            pass
        #its a variable
        if token.isalpha():
            return (Var(token),index+1)
        #starting expression (e1 op e2)
        if token == '(':
            left, i1 = parse_expression(index+1)
            operator = tokens[i1]
            right, i2 = parse_expression(i1+1)
            if tokens[i2]!=')':
                raise ValueError('no closing paranthesis')
            if operator == '+':
                return (left + right,i2+1)
            elif operator == '-':
                return (left-right,i2+1)
            elif operator == '*':
                return (left*right,i2+1)
            elif operator == '/':
                return (left/right,i2+1)
            else:
                raise ValueError("operator not binop")
    parsed_expression, _ = parse_expression(0)
    return parsed_expression

class SymbolicEvaluationError(Exception):
    """
    An expression indicating that something has gone wrong when evaluating a
    symbolic algebra expression.
    """
    pass

if __name__ == "__main__":
    # print(str(Div(Var('x'), Add(Var('y'), Var('z')))))
    # print(Num(3) / 'x')
    # print('x' / Num(3))
    # z = Add(Var('x'), Sub(Var('y'), Mul(Var('z'), Num(2))))
    # z = Add(Var('x'), Sub(Var('y'), Mul(Var('z'), Num(2))))
    # print(z)
    # print(z.evaluate({'x': 7, 'y': 3, 'z': 9}))
    # print(z.evaluate({'x': 3, 'y': 10, 'z': 2}))
    # x = Var('x')
    # y = Var('y')
    # z = 2*x - x*y + 3*y
    # print(z)
    # print(z.deriv('x'))
    # print(z.deriv('y'))
    # print(z.simplify())
    print(tokenize('6.101'))
    print(repr(make_expression('6.101')))
