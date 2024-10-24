from escaner import Escaner

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0 
        self.current_token = self.tokens[self.pos] if self.tokens else ('EOF', None)

    def advance(self):
        """Avanza al siguiente token"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = ('EOF', None)

    def match(self, expected_type, expected_value=None):
        """Verifica que el token actual coincida con el esperado y avanza."""
        token_type, token_value = self.current_token
        if token_type == expected_type and (expected_value is None or token_value == expected_value):
            self.advance()
        else:
            self.error(f"Se esperaba {expected_type} '{expected_value}', pero se encontró {token_type} '{token_value}'.")

    def error(self, message):
        """Maneja errores de sintaxis."""
        raise Exception(f"Error de sintaxis en el token {self.current_token}: {message}")

    def parse(self):
        """Punto de entrada para iniciar el análisis sintáctico."""
        self.parseProgram()
        print("Análisis sintáctico completado sin errores.")

    #metodos del parser

    def parseProgram(self):
        """Program → DeclarationList"""
        while self.current_token[0] != 'EOF':
            self.parseDeclaration()

    def parseDeclaration(self):
        """Declaration → Type Identifier DeclarationRest"""
        self.parseType()
        if self.current_token[0] == 'IDENTIFICADOR':
            self.match('IDENTIFICADOR')
            self.parseDeclarationRest()
        else:
            self.error("Se esperaba un identificador después del tipo en la declaración.")

    def parseDeclarationRest(self):
        """DeclarationRest → FunctionDeclRest | VarDeclRest"""
        if self.current_token == ('DELIM', '(') or self.current_token == ('DELIM', ';'):
            self.parseFunctionDeclRestOrVarDeclRest()
        else:
            self.parseVarDeclRest()

    def parseFunctionDeclRestOrVarDeclRest(self):
        """maneja la ambiguedad entre función sin paraametros y variable sin inicializacion."""
        if self.current_token == ('DELIM', '('):
            self.parseFunctionDeclRest()
        elif self.current_token == ('DELIM', ';'):
            # declaracion de variable sin inicializacion
            self.parseVarDeclRest()
        else:
            self.error("Se esperaba '(' para una función o ';' para una variable.")

    def parseFunctionDeclRest(self):
        """FunctionDeclRest → ( Params ) FunctionBody"""
        self.match('DELIM', '(')
        self.parseParams()
        self.match('DELIM', ')')
        # verificamos si la funcion termina con ; declaracion o tiene un cuerpo
        if self.current_token == ('DELIM', ';'):
            # Declaración de función sin cuerpo, termina con ;
            self.match('DELIM', ';')
        else:
            # definición de funcion con cuerpo
            self.parseBlock()

    def parseVarDeclRest(self, consume_semicolon=True):
        """VarDeclRest → ; | = Expression ;"""
        if self.current_token == ('DELIM', ';'):
            if consume_semicolon:
                self.match('DELIM', ';')
            else:
                # No consumimos el punto y coma aquí
                pass
        elif self.current_token == ('ASSIGN_OP', '='):
            self.match('ASSIGN_OP', '=')
            self.parseExpression()
            if consume_semicolon:
                self.match('DELIM', ';')
            else:
                # No consumimos el punto y coma aquí
                pass
        else:
            self.error("Se esperaba ';' o '=' en la declaración de variable")

    def parseType(self):
        """Type → SimpleType TypeArray"""
        self.parseSimpleType()
        self.parseTypeArray()

    def parseSimpleType(self):
        """SimpleType → integer | boolean | char | string | void"""
        token_type, token_value = self.current_token
        if token_type == 'PALABRA_CLAVE' and token_value in ('integer', 'boolean', 'char', 'string', 'void'):
            self.match('PALABRA_CLAVE')
        else:
            self.error("se esperaba un tipo simple (integer, boolean, char, string, void)")

    def parseTypeArray(self):
        """TypeArray → [ ] TypeArray | ε"""
        while self.current_token == ('DELIM', '['):
            self.match('DELIM', '[')
            self.match('DELIM', ']')
            #arrays pueden ser multidimensionales, continuamos el bucle

    def parseParams(self):
        """Params → ε | ParamList"""
        if self.current_token == ('DELIM', ')'):
            # ε
            return
        else:
            self.parseParamList()

    def parseParamList(self):
        """ParamList → Type Identifier ParamListRest"""
        self.parseType()
        if self.current_token[0] == 'IDENTIFICADOR':
            self.match('IDENTIFICADOR')
            self.parseParamListRest()
        else:
            self.error("se esperaba un identificador en la lista de paraametros")

    def parseParamListRest(self):
        """ParamListRest → , Type Identifier ParamListRest | ε"""
        while self.current_token == ('DELIM', ','):
            self.match('DELIM', ',')
            self.parseType()
            if self.current_token[0] == 'IDENTIFICADOR':
                self.match('IDENTIFICADOR')
            else:
                self.error("se esperaba un identificador en la lista de parametros")

    def parseBlock(self):
        """Block → { StatementList }"""
        self.match('DELIM', '{')
        self.parseStatementList()
        self.match('DELIM', '}')

    def parseStatementList(self):
        """StatementList → Statement StatementList | ε"""
        while self.current_token != ('DELIM', '}') and self.current_token[0] != 'EOF':
            self.parseStatement()

    def parseStatement(self):
        """Statement → VarDecl | IfStmt | ForStmt | WhileStmt | ReturnStmt | ExprStmt | PrintStmt | Block"""
        if self.current_token[0] == 'PALABRA_CLAVE':
            if self.current_token[1] in ('integer', 'boolean', 'char', 'string', 'void'):
                self.parseVarDecl()
            elif self.current_token[1] == 'if':
                self.parseIfStmt()
            elif self.current_token[1] == 'for':
                self.parseForStmt()
            elif self.current_token[1] == 'while':
                self.parseWhileStmt()
            elif self.current_token[1] == 'return':
                self.parseReturnStmt()
            elif self.current_token[1] == 'print':
                self.parsePrintStmt()
            else:
                self.error(f"Palabra clave inesperada '{self.current_token[1]}'.")
        elif self.current_token[0] == 'DELIM' and self.current_token[1] == '{':
            self.parseBlock()
        else:
            self.parseExprStmt()

    def parseVarDecl(self, consume_semicolon=True):
        """VarDecl → Type Identifier VarDeclRest"""
        self.parseType()
        if self.current_token[0] == 'IDENTIFICADOR':
            self.match('IDENTIFICADOR')
            self.parseVarDeclRest(consume_semicolon)
        else:
            self.error("se esperaba un identificador después del tipo en la declaración de variable")

    def parseExprStmt(self):
        """ExprStmt → Expression ; | ;"""
        if self.current_token == ('DELIM', ';'):
            self.match('DELIM', ';')
        else:
            self.parseExpression()
            self.match('DELIM', ';')

    # expresiones con precedencia correcta

    def parseExpression(self):
        """Expression → AssignmentExpression"""
        self.parseAssignmentExpression()

    def parseAssignmentExpression(self):
        """AssignmentExpression → LogicalOrExpression AssignmentExpressionRest"""
        self.parseLogicalOrExpression()
        if self.current_token == ('ASSIGN_OP', '='):
            self.match('ASSIGN_OP', '=')
            self.parseAssignmentExpression()

    def parseLogicalOrExpression(self):
        """LogicalOrExpression → LogicalAndExpression LogicalOrExpressionRest"""
        self.parseLogicalAndExpression()
        while self.current_token == ('OR_OP', '||'):
            self.match('OR_OP', '||')
            self.parseLogicalAndExpression()

    def parseLogicalAndExpression(self):
        """LogicalAndExpression → EqualityExpression LogicalAndExpressionRest"""
        self.parseEqualityExpression()
        while self.current_token == ('AND_OP', '&&'):
            self.match('AND_OP', '&&')
            self.parseEqualityExpression()

    def parseEqualityExpression(self):
        """EqualityExpression → RelationalExpression EqualityExpressionRest"""
        self.parseRelationalExpression()
        while self.current_token[0] in ('EQ', 'NE'):
            self.match(self.current_token[0], self.current_token[1])
            self.parseRelationalExpression()

    def parseRelationalExpression(self):
        """RelationalExpression → AdditiveExpression RelationalExpressionRest"""
        self.parseAdditiveExpression()
        while self.current_token[0] in ('LT', 'LE', 'GT', 'GE'):
            self.match(self.current_token[0], self.current_token[1])
            self.parseAdditiveExpression()

    def parseAdditiveExpression(self):
        """AdditiveExpression → MultiplicativeExpression AdditiveExpressionRest"""
        self.parseMultiplicativeExpression()
        while self.current_token[0] in ('ADD_OP', 'SUB_OP'):
            self.match(self.current_token[0], self.current_token[1])
            self.parseMultiplicativeExpression()

    def parseMultiplicativeExpression(self):
        """MultiplicativeExpression → UnaryExpression MultiplicativeExpressionRest"""
        self.parseUnaryExpression()
        while self.current_token[0] in ('MUL_OP', 'DIV_OP', 'MOD_OP'):
            self.match(self.current_token[0], self.current_token[1])
            self.parseUnaryExpression()

    def parseUnaryExpression(self):
        """UnaryExpression → ( - | ! ) UnaryExpression | PrimaryExpression"""
        if self.current_token[0] == 'SUB_OP' and self.current_token[1] == '-':
            self.match('SUB_OP', '-')
            self.parseUnaryExpression()
        elif self.current_token[0] == 'NOT_OP' and self.current_token[1] == '!':
            self.match('NOT_OP', '!')
            self.parseUnaryExpression()
        else:
            self.parsePrimaryExpression()

    def parsePrimaryExpression(self):
        """PrimaryExpression → IDENTIFICADOR PrimaryRest | Literal | ( Expression )"""
        token_type, token_value = self.current_token
        if token_type == 'IDENTIFICADOR':
            self.match('IDENTIFICADOR')
            self.parsePrimaryRest()
        elif token_type in ('ENTERO', 'CHAR', 'STRING'):
            self.match(token_type)
        elif token_type == 'PALABRA_CLAVE' and token_value in ('true', 'false'):
            # Literales booleanos
            self.match('PALABRA_CLAVE')
        elif self.current_token == ('DELIM', '('):
            self.match('DELIM', '(')
            self.parseExpression()
            self.match('DELIM', ')')
        else:
            self.error("Se esperaba una expresión primaria.")

    def parsePrimaryRest(self):
        """PrimaryRest → ( ArgumentListOpt ) | [ Expression ] | ε"""
        if self.current_token == ('DELIM', '('):
            self.match('DELIM', '(')
            self.parseArgumentListOpt()
            self.match('DELIM', ')')
        elif self.current_token == ('DELIM', '['):
            self.match('DELIM', '[')
            self.parseExpression()
            self.match('DELIM', ']')
        # Si no hay nada es ε

    def parseArgumentListOpt(self):
        """ArgumentListOpt → ArgumentList | ε"""
        if self.current_token != ('DELIM', ')'):
            self.parseArgumentList()

    def parseArgumentList(self):
        """ArgumentList → Expression ArgumentListRest"""
        self.parseExpression()
        while self.current_token == ('DELIM', ','):
            self.match('DELIM', ',')
            self.parseExpression()

    def parseIfStmt(self):
        """IfStmt → if ( Expression ) Statement ElseOpt"""
        self.match('PALABRA_CLAVE', 'if')
        self.match('DELIM', '(')
        self.parseExpression()
        self.match('DELIM', ')')
        self.parseStatement()
        self.parseElseOpt()

    def parseElseOpt(self):
        """ElseOpt → else Statement | ε"""
        if self.current_token == ('PALABRA_CLAVE', 'else'):
            self.match('PALABRA_CLAVE', 'else')
            self.parseStatement()
        # si no hay 'else', es ε

    def parseForStmt(self):
        """ForStmt → for ( ForInitOpt ; ExpressionOpt ; ExpressionOpt ) Statement"""
        self.match('PALABRA_CLAVE', 'for')
        self.match('DELIM', '(')
        self.parseForInitOpt()
        self.match('DELIM', ';')  #consumimos el punto y coma aqui
        self.parseExpressionOpt()
        self.match('DELIM', ';')
        self.parseExpressionOpt()
        self.match('DELIM', ')')
        self.parseStatement()

    def parseForInitOpt(self):
        """ForInitOpt → VarDecl | ExprStmt | ε"""
        if self.current_token[0] == 'PALABRA_CLAVE' and self.current_token[1] in ('integer', 'boolean', 'char', 'string', 'void'):
            self.parseVarDecl(consume_semicolon=False)
        elif self.current_token == ('DELIM', ';'):
            # ε (nada)
            pass
        else:
            self.parseExprStmt()

    def parseExpressionOpt(self):
        """ExpressionOpt → Expression | ε"""
        if self.current_token not in [('DELIM', ';'), ('DELIM', ')')]:
            self.parseExpression()
        # Si es ; o ), la expresion es opcional y puede estar ausente

    def parseWhileStmt(self):
        """WhileStmt → while ( Expression ) Statement"""
        self.match('PALABRA_CLAVE', 'while')
        self.match('DELIM', '(')
        self.parseExpression()
        self.match('DELIM', ')')
        self.parseStatement()

    def parseReturnStmt(self):
        """ReturnStmt → return ExpressionOpt ;"""
        self.match('PALABRA_CLAVE', 'return')
        if self.current_token != ('DELIM', ';'):
            self.parseExpression()
        self.match('DELIM', ';')

    def parsePrintStmt(self):
        """PrintStmt → print ( ArgumentListOpt ) ;"""
        self.match('PALABRA_CLAVE', 'print')
        self.match('DELIM', '(')
        self.parseArgumentListOpt()
        self.match('DELIM', ')')
        self.match('DELIM', ';')


if __name__ == '__main__':
    ruta_archivo = 'amigo.txt'  

    escaner = Escaner(ruta_archivo)
    escaner.escanear()

    parser = Parser(escaner.tokens)

    try:
        parser.parse()
    except Exception as e:
        print(e)