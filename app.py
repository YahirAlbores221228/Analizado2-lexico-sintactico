from flask import Flask, render_template, request
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

tokens = (
    'PACKAGE',
    'IMPORT',
    'FUNC',
    'PRINTLN',
    'IDENTIFIER',
    'STRING',
    'LPAREN',
    'RPAREN',
    'LLAVE_ABIERTA',
    'LLAVE_CERRADA',
    'DOT',
    'SEMICOLON',
)

reserved = {
    'package': 'PACKAGE',
    'import': 'IMPORT',
    'func': 'FUNC',
    'println': 'PRINTLN'
}

# Reglas de tokens
t_PACKAGE = r'package'
t_IMPORT = r'import'
t_FUNC = r'func'
t_PRINTLN = r'println'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LLAVE_ABIERTA = r'\{'
t_LLAVE_CERRADA = r'\}'
t_DOT = r'\.'
t_SEMICOLON = r';'

t_ignore = ' \t'

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = str(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

syntax_errors = []

# Gramática del análisis sintáctico
def p_program(p):
    '''program : package_clause import_clause function_clause'''
    p[0] = ('program', p[1], p[2], p[3])

def p_package_clause(p):
    '''package_clause : PACKAGE IDENTIFIER'''
    p[0] = ('package', p[2])

def p_import_clause(p):
    '''import_clause : IMPORT STRING'''
    p[0] = ('import', p[2])

def p_function_clause(p):
    '''function_clause : FUNC IDENTIFIER LPAREN RPAREN LLAVE_ABIERTA statements LLAVE_CERRADA'''
    p[0] = ('function', p[2], p[6])

def p_statements(p):
    '''statements : statement
                  | statement statements'''
    p[0] = ('statements', p[1], p[2] if len(p) > 2 else None)

def p_statement(p):
    '''statement : statement_print'''
    p[0] = p[1]

def p_statement_print(p):
    '''statement_print : IDENTIFIER DOT PRINTLN LPAREN STRING RPAREN SEMICOLON'''
    p[0] = ('println', p[1], p[3], p[5])

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
    token_counts = {
        'reserved': 0,
        'identifier': 0,
        'number': 0,
        'symbol': 0,
        'left_paren': 0,
        'right_paren': 0,
        'left_brace': 0,
        'right_brace': 0
    }
    token_info = []

    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append(tok)
        if tok.type in reserved.values():
            token_counts['reserved'] += 1
            token_info.append({'token': tok.value, 'type': 'reserved'})
        elif tok.type == 'IDENTIFIER':
            token_counts['identifier'] += 1
            token_info.append({'token': tok.value, 'type': 'identifier'})
        elif tok.type == 'NUMBER':
            token_counts['number'] += 1
            token_info.append({'token': tok.value, 'type': 'number'})
        elif tok.type in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'DOT', 'SEMICOLON']:
            token_counts['symbol'] += 1
            token_info.append({'token': tok.value, 'type': 'symbol'})
        elif tok.type == 'LPAREN':
            token_counts['left_paren'] += 1
            token_info.append({'token': tok.value, 'type': 'left_paren'})
        elif tok.type == 'RPAREN':
            token_counts['right_paren'] += 1
            token_info.append({'token': tok.value, 'type': 'right_paren'})
        elif tok.type == 'LLAVE_ABIERTA':
            token_counts['left_brace'] += 1
            token_info.append({'token': tok.value, 'type': 'left_brace'})
        elif tok.type == 'LLAVE_CERRADA':
            token_counts['right_brace'] += 1
            token_info.append({'token': tok.value, 'type': 'right_brace'})

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

    return render_template('index2.html', tokens=tokens, token_info=token_info, token_counts=token_counts, input_text=input_text, syntax_message=syntax_message)

if __name__ == '__main__':
    app.run(debug=True)
