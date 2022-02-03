# -----------------------------------------------------------------------------
# calc.py
#
# Expressions arithmétiques sans variables
# -----------------------------------------------------------------------------
import ply.lex as lex
import ply.yacc as yacc

reserved = {
    'print': 'PRINT'
}

tokens = [
             'NUMBER', 'MINUS',
             'PLUS', 'TIMES', 'DIVIDE',
             'LPAREN', 'RPAREN', 'AND', 'OR',
             'SEMICOLON', 'NAME', 'AFFECT',
             'COMPARE'
         ] + list(reserved.values())

# Tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_AND = r'\&'
t_OR = r'\|'
t_SEMICOLON = r';'
t_AFFECT = r'='
t_COMPARE = r'<=|<|>=|>|=='

precedence = (
    ('nonassoc', 'AFFECT'),
    ('right', 'AND', 'OR'),
    ('left', 'COMPARE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'DIVIDE', 'TIMES')
)

var = {}

def t_NAME(t):
    r"""[a-zA-Z_][a-zA-Z0-9_]*"""
    t.type = reserved.get(t.value, 'NAME')
    return t


def t_NUMBER(t):
    r"""\d+"""
    t.value = int(t.value)
    return t


# Ignored characters
t_ignore = " \t"


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lex.lex()


def p_bloc(p):
    """start : statement SEMICOLON start
    | statement SEMICOLON"""


def p_expression_print(p):
    """statement : PRINT LPAREN expression RPAREN"""
    print(p[3])


def p_statement_expr(p):
    """statement : expression"""


def p_expression_binop_plus(p):
    """expression : expression PLUS expression"""
    p[0] = p[1] + p[3]


def p_expression_binop_times(p):
    """expression : expression TIMES expression"""
    p[0] = p[1] * p[3]


def p_expression_binop_divide_and_minus(p):
    """expression : expression MINUS expression
    | expression DIVIDE expression"""
    if p[2] == '-':
        p[0] = p[1] - p[3]
    else:
        p[0] = p[1] / p[3]


def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]


def p_expression_number(p):
    """expression : NUMBER"""
    p[0] = p[1]


def p_expression_variable(p):
    """expression : NAME"""
    p[0] = var[p[1]]


def p_error(p):
    print("Syntax error at '%s'" % p.value)


def p_expression_binop_bool(p):
    """expression : expression AND expression
    | expression OR expression"""
    if p[2] == '&':
        p[0] = p[1] and p[3] != 0
    else:
        p[0] = p[1] or p[3] != 0


def p_expression_compare(p):
    """expression : expression COMPARE expression"""
    if p[2] == '<':
        p[0] = p[1] < p[3]
    elif p[2] == '<=':
        p[0] = p[1] <= p[3]
    elif p[2] == '>':
        p[0] = p[1] > p[3]
    elif p[2] == '>=':
        p[0] = p[1] >= p[3]
    elif p[2] == '==':
        p[0] = p[1] == p[3]


def p_expression_compare_mul(p):
    """expression : expression COMPARE expression COMPARE expression"""
    if p[2] != p[4]:
        return False
    if p[2] == '<':
        p[0] = p[1] < p[3] < p[5]
    elif p[2] == '<=':
        p[0] = p[1] <= p[3] <= p[5]
    elif p[2] == '>':
        p[0] = p[1] > p[3] > p[5]
    elif p[2] == '>=':
        p[0] = p[1] >= p[3] >= p[5]
    elif p[2] == '==':
        p[0] = p[1] == p[3] == p[5]


def p_expression_affect(p):
    """expression : NAME AFFECT expression"""
    var[p[1]] = p[3]


yacc.yacc()

s = input('calc > ')
yacc.parse(s)
