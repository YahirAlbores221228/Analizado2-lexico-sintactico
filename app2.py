from flask import Flask, render_template, request
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

tokens = (
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'IDENTIFIER',
    'SEMICOLON',
    'COMMA',
    'EQUALS',
    'LLAVE_ABIERTA',
    'LLAVE_CERRADA',
    'FOR',
    'SYSTEM',
    'OUT',
    'PRINTLN',
    'DOT',
    'LT',  # Menor que
    'LE',  # Menor o igual que
    'GT',  # Mayor que
    'GE',  # Mayor o igual que
    'EQ',  # Igual que
    'NE'   # Diferente de
)

reserved = {
    'for': 'FOR',
    'println': 'PRINTLN',
    'system': 'SYSTEM',
    'out': 'OUT'
}

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMICOLON = r';'
t_COMMA = r','
t_EQUALS = r'='
t_LLAVE_ABIERTA = r'\{'
t_LLAVE_CERRADA = r'\}'
t_DOT = r'\.'

t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_EQ = r'=='
t_NE = r'!='

t_ignore = ' \t'

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

syntax_errors = []

def p_program(p):
    '''program : statement
               | statement program'''
    p[0] = ('program', p[1], p[2] if len(p) > 2 else None)

def p_statement_for(p):
    '''statement : FOR LPAREN declaration SEMICOLON condition SEMICOLON increment RPAREN LLAVE_ABIERTA statements LLAVE_CERRADA'''
    p[0] = ('for', p[3], p[5], p[7], p[10])

def p_declaration(p):
    '''declaration : IDENTIFIER EQUALS expression'''
    p[0] = ('declaration', p[1], p[2], p[3])

def p_condition(p):
    '''condition : expression comparison_op expression'''
    p[0] = ('condition', p[1], p[2], p[3])

def p_comparison_op(p):
    '''comparison_op : LT
                     | LE
                     | GT
                     | GE
                     | EQ
                     | NE'''
    p[0] = p[1]

def p_increment(p):
    '''increment : IDENTIFIER PLUS PLUS
                 | IDENTIFIER MINUS MINUS'''
    p[0] = ('increment', p[1], p[2] + p[3])

def p_statements(p):
    '''statements : statement
                  | statement statements'''
    p[0] = ('statements', p[1], p[2] if len(p) > 2 else None)

def p_statement_print(p):
    '''statement : SYSTEM DOT OUT DOT PRINTLN LPAREN expression RPAREN SEMICOLON'''
    p[0] = ('println', p[1], p[3], p[5], p[7])

def p_expression_binop(p):
    '''expression : expression PLUS term
                  | expression MINUS term
                  | expression TIMES term
                  | expression DIVIDE term'''
    p[0] = (p[2], p[1], p[3])

def p_expression_term(p):
    'expression : term'
    p[0] = p[1]

def p_term_number(p):
    'term : NUMBER'
    p[0] = p[1]

def p_term_identifier(p):
    'term : IDENTIFIER'
    p[0] = p[1]

def p_error(p):
    if p:
        error_message = f"Syntax error at '{p.value}' on line {p.lineno}"
        print(error_message)
        syntax_errors.append(error_message)
    else:
        error_message = "Syntax error at EOF"
        print(error_message)
        syntax_errors.append(error_message)

parser = yacc.yacc()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    input_text = request.form['code']
    lexer.input(input_text)
    tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append(tok)

    global syntax_errors
    syntax_errors = []

    try:
        result = parser.parse(input_text)
        if not syntax_errors:
            syntax_message = "Estructura correcta"
        else:
            syntax_message = " ".join(syntax_errors)
    except Exception as e:
        result = None
        syntax_message = str(e)

    return render_template('index.html', tokens=tokens, result=result, input_text=input_text, syntax_message=syntax_message)

if __name__ == '__main__':
    app.run(debug=True)
