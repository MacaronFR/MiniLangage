from genereTreeGraphviz2 import printTreeGraph


class Stop(BaseException):
    a = 0


reserved = {
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'fun': 'FUN',
    'proc': 'PROC',
    'stop': 'STOP'
}

tokens = [
             'NUMBER', 'MINUS',
             'PLUS', 'TIMES', 'DIVIDE', 'AND', 'OR',
             'LPAREN', 'RPAREN', 'COMPARE', 'AFFECT', 'VAR', 'DELIM',
             'OPENBRACE', 'CLOSEBRACE', 'INC', 'DEC', 'ASSPLUS', 'ASSMINUS', 'ASSTIMES', 'ASSDIV',
             'OPENQUOTE', 'CLOSEQUOTE', 'ANY', 'DELIMPARAM', 'RBRACKET', 'LBRACKET'
         ] + list(reserved.values())

# Tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_AND = r'\&'
t_OR = r'\|'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_COMPARE = r'<=|<|>=|>|==|!='
t_AFFECT  = r'='
t_DELIM   = r';'
t_DELIMPARAM = r','
t_OPENBRACE = r'{'
t_CLOSEBRACE = r'}'
t_INC     = r'\+\+'
t_DEC     = r'--'
t_ASSPLUS = r'\+='
t_ASSMINUS= r'-='
t_ASSTIMES= r'\*='
t_ASSDIV  = r'/='
t_OPENQUOTE = r'«'
t_CLOSEQUOTE = r'»'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'

precedence = (
    ('left', 'COMPARE'),
    ('nonassoc', 'AFFECT', 'ASSPLUS', 'ASSMINUS', 'ASSTIMES', 'ASSDIV'),
    ('right', 'AND', 'OR'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'DIVIDE', 'TIMES'),
)

function = {}

procedure = {}


def t_VAR(t):
    r"""[a-zA-Z_][a-zA-Z0-9_]*"""
    t.type = reserved.get(t.value, 'VAR')
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Ignored characters
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lex.lex()


def p_start(p):
    """start : code"""
    p[0] = ('START', p[1])
    print('Arbre de dérivation = ', p[0])
    #printTreeGraph(p[1])
    evalCode(p[1])
    try:
        if 'main' in function:
            evalInst(function['main'][1], {})
        elif 'main' in procedure:
            evalInst(procedure['main'][1], {})
        else:
            print("No entry point")
    except Stop:
        return

def p_code(p):
    """code : function code
    | function"""
    if len(p) > 2:
        p[0] = ('code', p[1], p[2])
    else:
        p[0] = ('code', p[1])


def p_param(p):
    """param : VAR DELIMPARAM param
    | VAR"""
    if len(p) > 2:
        p[0] = ('param', p[1], p[3])
    else:
        p[0] = ('param', p[1])


def p_callparam(p):
    """callparam : expression DELIMPARAM callparam
    | expression"""
    if len(p) > 2:
        p[0] = ('param', p[1], p[3])
    else:
        p[0] = ('param', p[1])


def p_value(p):
    """value : expression
    | VAR"""
    p[0] = p[1]


def p_listvalue(p):
    """listvalue : value
    | value DELIMPARAM listvalue"""
    if len(p) > 2:
        p[0] = ('value', p[1], p[3])
    else:
        p[0] = ('value', p[1])


def p_array(p):
    """array : LBRACKET listvalue RBRACKET
    | LBRACKET RBRACKET"""
    if len(p) > 3:
        p[0] = ('array', p[2])
    else:
        p[0] = ('array', ('value'))


def p_function(p):
    """function : FUN VAR LPAREN param RPAREN OPENBRACE bloc CLOSEBRACE
    | FUN VAR LPAREN RPAREN OPENBRACE bloc CLOSEBRACE"""
    if len(p) > 8:
        p[0] = ('function', p[2], p[4], p[7])
    else:
        p[0] = ('function', p[2], ("param"), p[6])


def p_procedure(p):
    """function : PROC VAR LPAREN param RPAREN OPENBRACE bloc CLOSEBRACE
    | PROC VAR LPAREN RPAREN OPENBRACE bloc CLOSEBRACE"""
    if len(p) > 8:
        p[0] = ('procedure', p[2], p[4], p[7])
    else:
        p[0] = ('procedure', p[2], ("param"), p[6])


def p_bloc(p):
    """bloc : statement bloc
    | statement"""
    if len(p) > 2:
        p[0] = ('statement', p[1], p[2])
    else:
        p[0] = ('statement', p[1])


def p_statement_expr(p):
    """statement : expression DELIM
    | assign DELIM"""
    p[0] = p[1]


def p_statement_stop(p):
    """statement : STOP DELIM"""
    p[0] = 'stop'


def p_statement_if(p):
    """statement : ifstatement"""
    p[0] = p[1]


def p_ifstatement(p):
    """ifstatement : IF LPAREN expression RPAREN OPENBRACE bloc CLOSEBRACE
    | IF LPAREN expression RPAREN OPENBRACE bloc CLOSEBRACE ELSE OPENBRACE bloc CLOSEBRACE
    | IF LPAREN expression RPAREN OPENBRACE bloc CLOSEBRACE ELSE ifstatement"""
    if len(p) < 10:
        p[0] = ('if', p[3], p[6])
    elif len(p) < 11:
        p[0] = ('if', p[3], p[6], ('else', p[9]))
    else:
        p[0] = ('if', p[3], p[6], ('else', p[10]))


def p_statement_while(p):
    """statement : WHILE LPAREN expression RPAREN OPENBRACE bloc CLOSEBRACE"""
    p[0] = ('while', p[3], p[6])


def p_statement_for(p):
    'statement : FOR LPAREN assign DELIM expression DELIM bloc RPAREN OPENBRACE bloc CLOSEBRACE'
    p[0] = ('for', p[3], p[5], p[7], p[10])


def p_expression_print(p):
    'expression : PRINT LPAREN expression RPAREN'
    p[0] = ('print', p[3])


def p_expression_binop_bool(p):
    """expression : expression AND expression
    | expression OR expression"""
    if p[2] == '&':
        p[0] = ('and', p[1], p[3])
    else:
        p[0] = ('or', p[1], p[3])


def p_expression_compare(p):
    """expression : expression COMPARE expression"""
    p[0] = (p[2], p[1], p[3])


def p_expression_binop_plus(p):
    'expression : expression PLUS expression'
    p[0] = ('+', p[1] , p[3])


def p_expression_binop_minus(p):
    'expression : expression MINUS expression'
    p[0] = ('-', p[1] , p[3])


def p_expression_binop_times(p):
    'expression : expression TIMES expression'
    p[0] = ('*', p[1] , p[3])


def p_expression_binop_divide(p):
    'expression : expression DIVIDE expression'
    p[0] = ('/', p[1] , p[3])


def p_expression_inc(p):
    'expression : VAR INC'
    p[0] = ('++', p[1])


def p_expression_dec(p):
    'expression : VAR DEC'
    p[0] = ('--', p[1])


def p_expression_ass_plus(p):
    'expression : VAR ASSPLUS expression'
    p[0] = ('+=', p[1], p[3])


def p_expression_ass_minus(p):
    'expression : VAR ASSMINUS expression'
    p[0] = ('-=', p[1], p[3])


def p_expression_ass_times(p):
    'expression : VAR ASSTIMES expression'
    p[0] = ('*=', p[1], p[3])


def p_expression_ass_div(p):
    'expression : VAR ASSDIV expression'
    p[0] = ('/=', p[1], p[3])


def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2] 


def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]


def p_expression_var(p):
    'expression : VAR'
    p[0] = p[1]


def p_expression_array_access(p):
    """expression : VAR LBRACKET expression RBRACKET"""
    p[0] = ('arrayAccess', p[1], p[3])


def p_expression_call(p):
    """expression : VAR LPAREN callparam RPAREN
    | VAR LPAREN RPAREN"""
    if len(p) > 4:
        p[0] = ('call', p[1], p[3])
    else:
        p[0] = ('call', p[1], ('param'))


def p_assign(p):
    """assign : VAR AFFECT expression
    | VAR AFFECT array
    | VAR LBRACKET expression RBRACKET AFFECT expression"""
    if len(p) > 4:
        p[0] = ('assign', p[1], p[6], p[3])
    else:
        p[0] = ('assign', p[1], p[3])


def p_error(p):
    print("Syntax error at '%s'" % p.value)


import ply.yacc as yacc
yacc.yacc()

exprBin = [
    '+', '-', '*', '/', '==', '<', '>', '<=', '>='
]

exprUn = [
    '++', '--'
]

exprAss = {
    '+=', '-=', '*=', '/='
}


def evalExpr(t, scope):
    if type(t) == str:
        return scope[t]
    elif type(t) == tuple:
        if t[0] == '+':
            return evalExpr(t[1], scope) + evalExpr(t[2], scope)
        if t[0] == '-':
            return evalExpr(t[1], scope) - evalExpr(t[2], scope)
        if t[0] == '*':
            return evalExpr(t[1], scope) * evalExpr(t[2], scope)
        if t[0] == '/':
            return evalExpr(t[1], scope) / evalExpr(t[2], scope)
        if t[0] == '==':
            return evalExpr(t[1], scope) == evalExpr(t[2], scope)
        if t[0] == '!=':
            return evalExpr(t[1], scope) != evalExpr(t[2], scope)
        if t[0] == '<':
            return evalExpr(t[1], scope) < evalExpr(t[2], scope)
        if t[0] == '<=':
            return evalExpr(t[1], scope) <= evalExpr(t[2], scope)
        if t[0] == '>':
            return evalExpr(t[1], scope) > evalExpr(t[2], scope)
        if t[0] == '>=':
            return evalExpr(t[1], scope) >= evalExpr(t[2], scope)
        if t[0] == '++':
            scope[t[1]] += 1
            return scope[t[1]]
        if t[0] == '--':
            scope[t[1]] -= 1
            return scope[t[1]]
        if t[0] == 'call':
            new_scope = prepare_scope(t[2], t[1])
            if t[1] in function:
                try:
                    evalInst(function[t[1]], new_scope)
                finally:
                    if t[1] in new_scope:
                        return new_scope[t[1]]
                    raise ValueError("Function " + t[1] + " doesn't return value")
            elif t[1] in procedure:
                evalInst(procedure[t[1]], new_scope)
            else:
                print("Aucune fonction ou procédure appelé", t[1])
        if t[0] == 'array':
            if type(t[1]) == tuple:
                return getParam(t[1])
            else:
                return []
        if t[0] == 'arrayAccess':
            var = scope[t[1]]
            if type(var) == list:
                index = evalExpr(t[2], scope)
                if index < len(var):
                    return var[index]
                raise IndexError(str(index) + " out of range in array " + t[1])
            raise TypeError(t[1] + " is not an array")
    else:
        return t


def evalAssOp(t, scope):
    if t[0] == '+=':
        scope[t[1]] += evalExpr(t[2], scope)
    if t[0] == '-=':
        scope[t[1]] -= evalExpr(t[2], scope)
    if t[0] == '*=':
        scope[t[1]] *= evalExpr(t[2], scope)
    if t[0] == '/=':
        scope[t[1]] /= evalExpr(t[2], scope)


def evalInst(t, scope):
    try:
        if t[0] in exprBin:
            evalExpr(t[1], scope)
            evalExpr(t[2], scope)
        elif t[0] in exprUn:
            evalExpr(t, scope)
        else:
            if t[0] == 'call':
                try:
                    evalExpr(t, scope)
                except Stop:
                    return
            elif t[0] == 'assign':
                value = evalExpr(t[2], scope)
                if len(t) < 4:
                    scope[t[1]] = value
                else:
                    tmp = scope[t[1]]
                    index = evalExpr(t[3], scope)
                    if type(tmp) == list:
                        if len(tmp) <= index:
                            tmp.append(value)
                        else:
                            tmp[index] = value
                    else:
                        raise TypeError(t[1] + " is not an array")
            elif t[0] in exprAss:
                evalAssOp(t, scope)
            elif t[0] == 'print':
                print('CALC >' + str(evalExpr(t[1], scope)))
            elif t[0] == 'if':
                if evalExpr(t[1], scope):
                    evalInst(t[2], scope)
                elif len(t) > 3:
                    evalInst(t[3][1], scope)
            elif t[0] == 'while':
                while evalExpr(t[1], scope):
                    evalInst(t[2], scope)
            elif t[0] == 'for':
                evalInst(t[1], scope)
                while evalExpr(t[2], scope):
                    evalInst(t[4], scope)
                    evalInst(t[3], scope)
            elif t == 'stop':
                raise Stop
            else:
                evalInst(t[1], scope)
                if len(t) > 2:
                    evalInst(t[2], scope)
    except Stop:
        raise Stop


def prepare_scope(value, name):
    if name in function:
        return dict(zip(getParam(function[name][0]), getParam(value)))
    elif name in procedure:
        return dict(zip(getParam(procedure[name][0]), getParam(value)))


def getParam(t):
    if len(t) == 2:
        return [t[1]]
    else:
        return [t[1]] + getParam(t[2])


def evalCode(t):
    if t[0] == 'code':
        evalCode(t[1])
        if len(t) > 2:
            evalCode(t[2])
    elif t[0] == 'function':
        if not check_function_name(t[1]):
            print("Function", t[1], "already defined")
            return
        if check_function(t[1], t[3]):
            function[t[1]] = (t[2], t[3])
        else:
            print("Error function", t[1], "don't return any value")
    elif t[0] == 'procedure':
        if not check_function_name(t[1]):
            print("Procedure", t[1], "already defined")
            return
        if not check_function(t[1], t[3]):
            procedure[t[1]] = (t[2], t[3])
        else:
            print("Error procedure", t[1], "return a value")


def check_function_name(name):
    return name not in function and name not in procedure


def check_function(name, body):
    while body[0] == 'statement':
        if body[1][0] == 'assign':
            if body[1][1] == name:
                return True
            elif len(body) == 3:
                body = body[2]
        elif len(body) == 3:
            body = body[2]
        else:
            break
    return False


s = 'proc test5(){' \
    '   print(67);' \
    '}' \
    '' \
    'fun main(){' \
    '   y = [];' \
    '   y[0] = 8;' \
    '   z = [5,6,7,8];' \
    '   z[1+1] = 6 + 7;' \
    '   z[test(1,0)] = test(5,6);' \
    '   print(z[1]);' \
    '   print(y[1-1]);'\
    '   x=1;' \
    '   print(1<=1);' \
    '   x=6+4;print(x);' \
    '   if(x==6){' \
    '      x=7;' \
    '   }else if(x == 4){' \
    '       x=9;' \
    '   }else if(x == 10){' \
    '       x=3;' \
    '   }else{' \
    '       x = 24;' \
    '   }' \
    '   print(x);' \
    '   while(x<15){' \
    '       x*=2;' \
    '   }' \
    '   print(x);' \
    '   for(i=0;i<10;i++;print(i);){' \
    '       print(i);' \
    '   }' \
    '   print(test(5,7));' \
    '   main = x;' \
    '   stop;' \
    '   print(1);' \
    '}' \
    '' \
    'fun test(ola, ole){' \
    '   test = ola + ole;' \
    '   print(4);' \
    '   stop;' \
    '   print(5);' \
    '}'

yacc.parse(s)
