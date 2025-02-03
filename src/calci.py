from dataclasses import dataclass
from collections.abc import Iterator
from more_itertools import peekable
from typing import Optional, Any
from tokens import  *
from context import Context


class AST:
    """
    Abstract Syntax Tree (AST) class.

    This class represents the abstract syntax tree used in the compiler.
    It serves as a base class for all nodes in the AST.
    """

    pass

class ABT: #unused for the time being
    """
    ABT (Abstract Binding Tree) class.

    This class represents an abstract binding tree used in the compilation process.
    It is designed to handle the structure and operations related to the binding of
    variables and expressions in a compiler.
    """
    pass

@dataclass
class Binding(AST):
    name: str
    dtype: Optional[str]
    value: AST

        
@dataclass
class Variable(AST):
    name: str
    
    def eval(self,context):
        return context[self.name]

@dataclass
class BinOp(AST):
    op: str
    left: AST
    right: AST


@dataclass
class UnaryOp(AST):
    op: str
    val: AST


@dataclass
class Number(AST):
    val: str


@dataclass
class String(AST):
    val: str

@dataclass
class Display(AST):
    val: any


@dataclass
class CompoundAssignment(AST):
    var_name: str
    op: str
    value: AST


def e(tree: AST, context: Optional[Context] = None) -> Any:
    if context is None:
        context = Context()
    match tree:
        case Number(v):
            return int(v)
        case String(s):
            return s
        case BinOp("+", l, r):
            return e(l, context) + e(r, context)
        case BinOp("*", l, r):
            return e(l, context) * e(r, context)
        case BinOp("-", l, r):
            return e(l, context) - e(r, context)
        case BinOp("÷", l, r):
            return e(l,context) / e(r,context)
        case BinOp("/", l, r):
            return e(l, context) / e(r, context)
        case BinOp("<", l, r):
            return e(l, context) < e(r, context)
        case BinOp(">", l, r):
            return e(l, context) > e(r, context)
        case BinOp("==", l, r):
            return e(l, context) == e(r, context)
        case BinOp("!=", l, r):
            return e(l, context) != e(r, context)
        case BinOp("<=", l, r):
            return e(l, context) <= e(r, context)
        case BinOp(">=", l, r):
            return e(l, context) >= e(r, context)
        case BinOp("%", l, r):
            return e(l, context) % e(r, context)
        case UnaryOp("~", val):
            return ~e(val, context)
        case UnaryOp("!", val):
            return not e(val, context)
        case CompoundAssignment(var_name, op, value):
            var_value = context.get_variable(var_name).value
            context.update_variable(var_name, e(BinOp(op[0], Number(var_value), value), context))
            return context  # temporary return value -> will be removed later
        case If(cond, sat, else_):
            return e(sat, context) if e(cond, context) else e(else_, context)
        case Display(val):
            return print(e(val, context))
        case Binding(name, dtype, value):
            context.add_variable(name, e(value, context), dtype)
            return context  # temporary return value -> will be removed later

class Token:
    pass


@dataclass
class VarToken(Token):
    var_name : str

@dataclass
class NumberToken(Token):
    v: str


@dataclass
class OperatorToken(Token):
    o: str


@dataclass
class StringToken(Token):
    s: str


@dataclass
class KeywordToken(Token):
    w: str


@dataclass
class TypeToken(Token):
    t: str



@dataclass
class If(AST):
    c: AST
    t: AST
    e: AST = None


def lex(s: str) -> Iterator[Token]:
    i = 0
    prev_char = None
    prev_token= None
    while True:
        while i < len(s) and s[i].isspace():
            i = i + 1

        if i >= len(s):
            return

        if s[i].isalpha():
            t = s[i]
            i = i + 1
            while i < len(s) and s[i].isalpha():
                t = t + s[i]
                i = i + 1
            if t in keyword_tokens:
                yield KeywordToken(t)
            elif t in base_type_tokens:
                yield TypeToken(t)
            else:
                yield VarToken(t)
        elif s[i] == "'" or s[i] == '"':
            quote = s[i]
            i = i + 1
            t = ""
            while i < len(s) and s[i] != quote:
                t = t + s[i]
                i = i + 1
            if i >= len(s):
                raise SyntaxError(f"Expected {quote}")
            i = i + 1
            yield StringToken(t)

        elif s[i].isdigit():
            t = s[i]
            prev_char = s[i]
            i = i + 1
            while i < len(s) and s[i].isdigit():
                t = t + s[i]
                i = i + 1
            yield NumberToken(t)
        
        # Single-line and Inline comments: /~ ... ~/
        elif s[i:i+2] == "/~":
            i += 2  # skip "/~"
            while i < len(s) and s[i:i+2] != "~/":
                i += 1
            i += 2  # skip "~/"
            continue 

        # Multi-line comments: /~ { ... } ~/
        elif s[i:i+3] == "/~{":
            i += 3  # skip "/~{"
            while i < len(s) and s[i:i+3] != "}~/":
                i += 1
            i += 3  # skip "}~/"
            continue 
        
        else:
            match t := s[i]:
                case "-":
                    if (s[i+1]=="="):
                        i=i+2
                        yield OperatorToken("-=")
                    elif (
                        prev_char is None or prev_char in "+-*/(<>!=%"
                    ):  # check if it is a negative number
                        prev_char = s[i]
                        i = i + 1
                        yield NumberToken("-" + s[i])
                        i = i + 1
                    else:  # check if it is a token
                        prev_char = s[i]
                        i = i + 1
                        yield OperatorToken(t)
                case t if t in base_operator_tokens:
                    prev_char = s[i]
                    i = i + 1
                    if i<len(s) and (t + s[i]) in top_level_operator_tokens:
                        prev_char = s[i]
                        i = i + 1
                        yield OperatorToken(t + prev_char)
                    else:
                        yield (OperatorToken(t))


def parse(s: str) -> AST:

    t = peekable(lex(s))

    def expect(what: Token):
        if t.peek(None) == what:
            next(t)
            return
        raise SyntaxError(f"Expected {what} got {t.peek(None)}")
    
    def expect_any(expected_tokens: list[Token]):
        next_token = t.peek(None)  

        if next_token.o in expected_tokens:
            next(t)  
            return
        
        raise SyntaxError(f"Expected one of {expected_tokens}, but got {next_token}")

    def parse_display():
        ast=parse_var()
        while True:
            match t.peek(None):
                case KeywordToken("display"):
                    next(t)
                    ast=Display(parse_var())
                case _:
                    return ast
    
    def parse_var(): #for var declaration
        ast=parse_update_var()
        while True:
            match t.peek(None):
                case KeywordToken("var"):
                    next(t)
                    dtype=None
                    if isinstance(t.peek(None), TypeToken):
                        dtype= t.peek(None).t
                        next(t)
                    # print(t.peek(None))
                    if isinstance(t.peek(None), VarToken):
                        name = t.peek(None).var_name
                        next(t) 
                    # print(t.peek(None))
                    expect(OperatorToken("="))
                    # print(t.peek(None))
                    value = parse_var()
                    ast=Binding(name, dtype, value)
                case _:
                    return ast
    def parse_update_var(): # for updating var
        ast =parse_if()
        while True:
            match t.peek(None):
                case VarToken(var_name):
                    next(t)
                    if isinstance(t.peek(None),OperatorToken) and t.peek(None).o in compound_assigners:
                        op=t.peek(None).o
                        next(t)
                        value=parse_if()
                        ast=CompoundAssignment(var_name,op,value)
                    else:
                        return ast
                case _ :
                    return ast
    def parse_if():
        match t.peek(None):
            case KeywordToken("if"):
                next(t)
                cond = parse_if()
                expect(KeywordToken("then"))
                then = parse_if()
                expect(KeywordToken("else"))
                else_ = parse_if()
                expect(KeywordToken("end"))
                return If(cond, then, else_)
            case _:
                return parse_cmp()

    def parse_cmp():
        ast = parse_sub()
        while True:
            match t.peek(None):
                case OperatorToken("<"):
                    next(t)
                    ast = BinOp("<", ast, parse_sub())
                case OperatorToken(">"):
                    next(t)
                    ast = BinOp(">", ast, parse_sub())
                case OperatorToken("=="):
                    next(t)
                    ast = BinOp("==", ast, parse_sub())
                case OperatorToken("!="):
                    next(t)
                    ast = BinOp("!=", ast, parse_sub())
                case OperatorToken("<="):
                    next(t)
                    ast = BinOp("<=", ast, parse_sub())
                case OperatorToken(">="):
                    next(t)
                    ast = BinOp(">=", ast, parse_sub())
                case _:
                    return ast

    def parse_sub():
        ast = parse_add()
        while True:
            match t.peek(None):
                case OperatorToken("-"):
                    next(t)
                    ast = BinOp("-", ast, parse_add())
                case _:
                    return ast

    def parse_add():
        ast = parse_mul()
        while True:
            match t.peek(None):
                case OperatorToken("+"):
                    next(t)
                    ast = BinOp("+", ast, parse_mul())
                case _:
                    return ast

    def parse_mul():
        ast = parse_modulo()
        while True:
            match t.peek(None):
                case OperatorToken("*"):
                    next(t)
                    ast = BinOp("*", ast, parse_modulo())
                case _:
                    return ast
    def parse_modulo():
        ast =parse_div_slash()
        while True:
            match t.peek(None):
                case OperatorToken("%"):
                    next(t)
                    ast=BinOp("%",ast,parse_div_slash())
                case _:
                    return ast

    def parse_div_slash():
        ast = parse_div_dot()
        while True:
            match t.peek(None):
                case OperatorToken("/"):
                    next(t)
                    ast = BinOp("/", ast, parse_div_dot())
                case _:
                    return ast

    def parse_div_dot():
        ast = parse_brackets()
        while True:
            match t.peek(None):
                case OperatorToken("÷"):
                    next(t)
                    ast = BinOp("÷", ast, parse_brackets())
                case _:
                    return ast

    def parse_brackets():
        while True:
            match t.peek(None):
                case OperatorToken("("):
                    next(t)
                    ast = parse_display()
                    match t.peek(None):
                        case OperatorToken(")"):
                            next(t)
                            return ast
                        case _:
                            raise SyntaxError(f"Expected ')' got {t.peek(None)}")
                case _:
                    return parse_string()

    def parse_string(): # while True may be included in future
        match t.peek(None):
            case StringToken(s):
                next(t)
                return String(s)
            case _:
                return parse_atom()

    def parse_atom(): # while True may be included in future
        match t.peek(None):
            case NumberToken(v):
                next(t)
                return Number(v)

    return parse_display()


if __name__ == "__main__":
    # expression=" (5-4)*5+ (8-2)/3"
    # print(parse(expression))
    # print(e(parse(expression)))
    # simple_exp=" 3 *(3+1*(4-1)) /2"
    # simple_exp=" -3 + 7 + (2+8)/5 - (2*(4-3))"
    # print(parse(simple_exp))
    # print(e(parse(simple_exp)))
    # sample_exp="if 2 < 3 then 0 end"
    # print(parse("if 2 < 3 then 0+5 else 1*6 end"))
    # print(e(parse("if 2 < 3 then 0+5 else 1*6 end")))
    # expr = "display 2+1 "
    # expr = "display 0<= 1 >=2 "
    context=Context()
    expr = " display( var integer x= 3+ 7 -1)"
    compound_assignment= "display (x-=2)"
    for t in lex(expr):
        print(t)
    # t = peekable(lex(expr))
    # print(t.peek(None))
    # next(t)
    # print(t.peek(None))
    print("Parsed expression:")
    print(parse(expr))
    print("Evaluated expression:")
    e(parse(expr),context)
    for t in lex(compound_assignment):
        print(t)
    print("Parsed expression:")
    print(parse(compound_assignment))
    print("Evaluated expression:")
    e(parse(compound_assignment),context)

    # loop <condition> then <statement> end
    # int32 x=2
