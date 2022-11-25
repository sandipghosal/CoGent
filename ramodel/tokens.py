##############################
# TOKENS
##############################


ASSIGN      =   'ASSIGN'    # assignment
BOOL        =   'BOOL'      # boolean variable
ID          =   'ID'        # variable identifier
SPACE       =   'SPACE'     # ' '
COLON       =   'COLON'     # :
COMMA       =   'COMMA'     # ,
SEMICOLON   =   'SEMICOLON' # ;
LPAREN      =   'LPAREN'    # ( bracket
RPAREN      =   'RPAREN'    # ) bracket
COMPARE     =   'COMPARE'   # == operator
NEQ         =   'NEQ'       # != operator
AND         =   'AND'       # && operator
OR          =   'OR'        # || operator
NOT         =   'NOT'       # ! operator


token_expr = [
    (r' +',         SPACE),
    (r':=',         ASSIGN),
    (r'\=',         ASSIGN),
    (r'\(',         LPAREN),
    (r'\)',         RPAREN),
    (r'True',       BOOL),
    (r'False',      BOOL),
    (r'==',         COMPARE),
    (r':',          COLON),
    (r',',          COMMA),
    (r';',          SEMICOLON),
    (r'!=',         NEQ),
    (r'&',          AND),
    (r'and',        AND),
    (r'\|',         OR),
    (r'or',         OR),
    (r'!',          NOT),
    (r'not',        NOT),
    (r'[A-Za-z_][A-Za-z0-9_]*',  ID)
]