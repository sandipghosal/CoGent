##############################
# TOKENS
##############################


# List of delimiters
BOOL        =   'BOOL'        # boolean variable
ID          =   'ID'        # variable identifier
SPACE       =   'SPACE'       # ' '
NEWLINE     =   'NEWLINE'     # \n
TAB         =   'TAB'         # \t
COLON       =   'COLON'       # :
COMMA       =   'COMMA'       # ,
SRBRACKET   =   'SRBRACKET'   # ]
SLBRACKET   =   'SLBRACKET'   # [
CLBRACKET   =   'CLBRACKET'   # {
CRBRACKET   =   'CRBRACKET'   # }
DOT         =   'DOT'         # .
EOF         =   'EOF'

# List of operators
PLUS        =   'PLUS'    # + operator
MINUS       =   'MINUS'   # - operator
MUL         =   'MUL'     # * operator
DIV         =   'DIV'     # / operator
MOD         =   'MOD'     # % operator
LPAREN      =   'LPAREN'  # ( bracket
RPAREN      =   'RPAREN'  # ) bracket
COMPARE     =   'COMPARE' # == operator
LEQ         =   'LEQ'     # <= operator
GEQ         =   'GEQ'     # >= operator
GTHAN       =   'GTHAN'   # > operator
LTHAN       =   'LTHAN'   # < operator
NEQ         =   'NEQ'     # != operator
AND         =   'AND'     # && operator
OR          =   'OR'      # || operator
NOT         =   'NOT'     # ! operator
XOR         =   'XOR'     # ^ operator
SQUOTE      =   'SQUOTE'  # ' single quote
DQUOTE      =   'DQUOTE'  # '' double quote
IMPLY       =   'IMPLY'   # => implication



token_expr = [
    (r' +',         SPACE),
    (r'\t+',        TAB),
    # (r'#[^\n]+',    COMMENT),
    (r'\n',         NEWLINE),
    (r'true',       BOOL),
    (r'True',       BOOL),
    (r'TRUE',       BOOL),
    (r'false',      BOOL),
    (r'False',      BOOL),
    (r'FALSE',      BOOL),
    # (r'import\s?(\w+)', IMPORT),
    # (r'Thread',     THREAD),
    (r'==',         COMPARE),
    # (r'pass',       PASS),
    # (r'return',     RETURN),
    # (r'\=',         ASSIGN),
    (r'\(',         LPAREN),
    (r'\)',         RPAREN),
    (r'\+',         PLUS),
    (r'\-',         MINUS),
    (r'\*',         MUL),
    (r'\^',         XOR),
    (r'/',          DIV),
    (r'%',          MOD),
    (r'<=',         LEQ),
    (r'>=',         GEQ),
    (r'=>',         IMPLY),
    (r'<',          LTHAN),
    (r'>',          GTHAN),
    (r'!=',         NEQ),
    (r'&&',         AND),
    (r'&',          AND),
    (r'and',        AND),
    (r'And',        AND),
    (r'\|\|',       OR),
    (r'\|',         OR),
    (r'or',         OR),
    (r'Or',         OR),
    (r'!',          NOT),
    (r'~',          NOT),
    (r'not',        NOT),
    (r'Not',        NOT),
    # (r'if',         IF),
    # (r'else',       ELSE),
    # (r'endif',      ENDIF),
    # (r'while',      WHILE),
    # (r'ewhile',     EWHILE),
    # (r'def',        FDEF),
    # (r'endef',      ENDEF),
    (r':',          COLON),
    (r',',          COMMA),
    (r'\.',         DOT),
    (r'\'',         SQUOTE),
    (r'\"',         DQUOTE),
    (r'\[',         SLBRACKET),
    (r'\]',         SRBRACKET),
    (r'\{',         CLBRACKET),
    (r'\}',         CRBRACKET),

    # Regex for float, integer or variable
    # (r'(\'[A-Za-z0-9]+\'|\"[A-Za-z0-9]+\")', STRING),
    # (r'[0-9]+[.][0-9]+',         FLOAT),
    # (r'[0-9]+',                  INT),
    # (r'downgrade',               DOWNGRADE),
    (r'[A-Za-z_][A-Za-z0-9_]*',  ID)

]