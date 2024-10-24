class Escaner:
    def __init__(self, ruta_archivo):
        with open(ruta_archivo, 'r') as archivo:
            self.datos_entrada = archivo.read()
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.contador_errores = 0
        self.tokens = []  # Lista para almacenar los tokens

    def obtener_caracter(self):
        """Obtiene el siguiente caracter y avanza el puntero"""
        if self.posicion < len(self.datos_entrada):
            caracter = self.datos_entrada[self.posicion]
            self.posicion += 1
            if caracter == '\n':
                self.linea += 1
                self.columna = 1
            else:
                self.columna += 1
            return caracter
        return None  

    def ver_caracter(self):
        """Mira el siguiente carácter sin mover el puntero"""
        if self.posicion < len(self.datos_entrada):
            return self.datos_entrada[self.posicion]
        return None

    def saltar_espacios(self):
        """Salta espacios en blanco y comentarios"""
        while True:
            caracter = self.ver_caracter()
            if caracter in [' ', '\t', '\n']:
                self.obtener_caracter()  # Consumir espacio en blanco
            elif caracter == '/' or caracter == '#':  # Posible comentario
                self.manejar_comentario_o_division()
            else:
                break

    def manejar_comentario_o_division(self):
        """Maneja comentarios estilo C, C++ o el operador de división"""
        caracter = self.obtener_caracter()
        if caracter == '/':
            siguiente_caracter = self.ver_caracter()
            if siguiente_caracter == '/':  # Comentario de una línea estilo C++
                while self.obtener_caracter() != '\n':
                    continue  # Ignorar todo hasta el final de la línea
            elif siguiente_caracter == '*':  # Comentario de varias líneas estilo C
                self.obtener_caracter()  # Consumir '*'
                while True:
                    caracter = self.obtener_caracter()
                    if caracter is None:  # Fin del archivo sin cierre de comentario
                        print(f"Error: Comentario sin cerrar en la línea {self.linea}, columna {self.columna}")
                        self.contador_errores += 1
                        return
                    if caracter == '*' and self.ver_caracter() == '/':
                        self.obtener_caracter()  # Consumir '/'
                        break
            else:
                # Si no es un comentario, es el operador de división
                print(f"DEBUG SCAN - DIV_OP [ / ] found at ({self.linea}:{self.columna-1})")
                return ('DIV_OP', '/')
        elif caracter == '#':  # Comentario de una línea estilo Python
            while self.obtener_caracter() != '\n':
                continue  # Ignorar todo hasta el final de la línea

    def obtener_token(self):
        """Identifica el siguiente token válido"""
        self.saltar_espacios()
        columna_inicial = self.columna  # Guardar la columna inicial
        caracter = self.ver_caracter()
        
        if caracter is None:
            return None  # Fin del archivo
        
        caracter = self.obtener_caracter()
        
        # Identificadores y palabras clave
        if caracter.isalpha() or caracter == '_':  # Empieza con letra o '_'
            return self.manejar_identificador_o_palabra_clave(caracter, columna_inicial)
        
        # Números enteros
        if caracter.isdigit():
            return self.manejar_entero(caracter, columna_inicial)
        
        # Caracteres
        if caracter == "'":
            return self.manejar_caracter(columna_inicial)

        # Cadenas
        if caracter == '"':
            return self.manejar_cadena(columna_inicial)

        # Operadores y delimitadores adicionales
        if caracter in [':', '{', '}', '[', ']', ',', ';', '>', '<', '=', '+', '-', '*', '/', '(', ')', '$', '%', '^', '!', '&', '|']:
            return self.manejar_operador_o_delimitador(caracter, columna_inicial)
        
        # Error léxico
        print(f"DEBUG SCAN - Lexical error: unexpected character '{caracter}' at line {self.linea}, column {self.columna}")
        self.contador_errores += 1
        return self.obtener_token()  # Continuar después del error

    def manejar_identificador_o_palabra_clave(self, caracter, columna_inicial):
        """Procesa un identificador o palabra clave"""
        identificador = caracter
        while self.ver_caracter() is not None and (self.ver_caracter().isalnum() or self.ver_caracter() == '_'):
            identificador += self.obtener_caracter()
        
        # Verificar si es una palabra clave reservada
        palabras_clave = ['array', 'boolean', 'char', 'else', 'false', 'for', 'function', 'if', 'integer', 'print', 'return', 'string', 'true', 'void', 'while']
        if identificador in palabras_clave:
            print(f"DEBUG SCAN - PALABRA_CLAVE [ {identificador} ] found at ({self.linea}:{columna_inicial})")
            return ('PALABRA_CLAVE', identificador)
        else:
            print(f"DEBUG SCAN - IDENTIFICADOR [ {identificador} ] found at ({self.linea}:{columna_inicial})")
            return ('IDENTIFICADOR', identificador)

    def manejar_entero(self, caracter, columna_inicial):
        """Procesa un número entero"""
        numero = caracter
        while self.ver_caracter() is not None and self.ver_caracter().isdigit():
            numero += self.obtener_caracter()
        
        # Verificación para evitar casos invalidos como como 123abc 
        if self.ver_caracter() is not None and self.ver_caracter().isalpha():
            print(f"DEBUG SCAN - Lexical error: invalid number '{numero}{self.ver_caracter()}' at line {self.linea}, column {self.columna}")
            self.contador_errores += 1
            while self.ver_caracter() is not None and self.ver_caracter().isalnum():
                self.obtener_caracter()  # Consumir caracteres invalidos
            return self.obtener_token()  # Continuar después del error
        print(f"DEBUG SCAN - ENTERO [ {numero} ] found at ({self.linea}:{columna_inicial})")
        return ('ENTERO', int(numero))

    def manejar_caracter(self, columna_inicial):
        """Procesa un carácter entre comillas simples"""
        caracter = self.obtener_caracter()  # Obtener el carácter dentro de las comillas simples
        if self.obtener_caracter() != "'":
            print(f"DEBUG SCAN - Error: Character not closed at line {self.linea}, column {self.columna}")
            self.contador_errores += 1
            return None
        print(f"DEBUG SCAN - CHAR [ '{caracter}' ] found at ({self.linea}:{columna_inicial})")
        return ('CHAR', caracter)

    def manejar_cadena(self, columna_inicial):
        """Procesa una cadena entre comillas dobles"""
        cadena = ''
        while True:
            caracter = self.obtener_caracter()
            if caracter == '"':  # Final de la cadena
                break
            if caracter is None or caracter == '\n':
                print(f"DEBUG SCAN - Error: String not closed at line {self.linea}, column {self.columna}")
                self.contador_errores += 1
                return None
            cadena += caracter
        print(f"DEBUG SCAN - STRING [ \"{cadena}\" ] found at ({self.linea}:{columna_inicial})")
        return ('STRING', cadena)

    def manejar_operador_o_delimitador(self, caracter, columna_inicial):
        """Procesa operadores y delimitadores"""
        siguiente_caracter = self.ver_caracter()

        # Manejar operadores dobles como &&, ||, >=, <=, ==, !=
        if caracter == '&':
            if siguiente_caracter == '&':
                self.obtener_caracter()  # Consumir el segundo '&'
                print(f"DEBUG SCAN - AND_OP [ && ] found at ({self.linea}:{columna_inicial})")
                return ('AND_OP', '&&')
            else:
                print(f"DEBUG SCAN - Lexical error: unexpected character '&' at line {self.linea}, column {self.columna}")
                self.contador_errores += 1
                return None

        elif caracter == '|':
            if siguiente_caracter == '|':
                self.obtener_caracter()  # Consumir el segundo '|'
                print(f"DEBUG SCAN - OR_OP [ || ] found at ({self.linea}:{columna_inicial})")
                return ('OR_OP', '||')
            else:
                print(f"DEBUG SCAN - Lexical error: unexpected character '|' at line {self.linea}, column {self.columna}")
                self.contador_errores += 1
                return None

        elif caracter == '>':
            if siguiente_caracter == '=':
                self.obtener_caracter()  # Consumir el '='
                print(f"DEBUG SCAN - GE [ >= ] found at ({self.linea}:{columna_inicial})")
                return ('GE', '>=')
            else:
                print(f"DEBUG SCAN - GT [ > ] found at ({self.linea}:{columna_inicial})")
                return ('GT', '>')

        elif caracter == '<':
            if siguiente_caracter == '=':
                self.obtener_caracter()  # Consumir el '='
                print(f"DEBUG SCAN - LE [ <= ] found at ({self.linea}:{columna_inicial})")
                return ('LE', '<=')
            else:
                print(f"DEBUG SCAN - LT [ < ] found at ({self.linea}:{columna_inicial})")
                return ('LT', '<')

        elif caracter == '=':
            if siguiente_caracter == '=':
                self.obtener_caracter()  # Consumir el '='
                print(f"DEBUG SCAN - EQ [ == ] found at ({self.linea}:{columna_inicial})")
                return ('EQ', '==')
            else:
                print(f"DEBUG SCAN - ASSIGN_OP [ = ] found at ({self.linea}:{columna_inicial})")
                return ('ASSIGN_OP', '=')

        elif caracter == '!':
            if siguiente_caracter == '=':
                self.obtener_caracter()  # Consumir el '='
                print(f"DEBUG SCAN - NE [ != ] found at ({self.linea}:{columna_inicial})")
                return ('NE', '!=')
            else:
                print(f"DEBUG SCAN - NOT_OP [ ! ] found at ({self.linea}:{columna_inicial})")
                return ('NOT_OP', '!')

        # Diccionario de operadores y delimitadores simples
        operadores_y_delimitadores = {
            '+': 'ADD_OP',
            '-': 'SUB_OP',
            '*': 'MUL_OP',
            '/': 'DIV_OP',
            '%': 'MOD_OP',
            '^': 'EXP_OP',
            '(': 'DELIM',
            ')': 'DELIM',
            ';': 'DELIM',
            '$': 'DELIM',
            ':': 'DELIM',
            '{': 'DELIM',
            '}': 'DELIM',
            '[': 'DELIM',
            ']': 'DELIM',
            ',': 'DELIM'
        }

        if caracter in operadores_y_delimitadores:
            token_type = operadores_y_delimitadores[caracter]
            print(f"DEBUG SCAN - {token_type} [ {caracter} ] found at ({self.linea}:{columna_inicial})")
            return (token_type, caracter)

        # Si no es ninguno de los operadores o delimitadores esperados
        print(f"DEBUG SCAN - Lexical error: unexpected character '{caracter}' at line {self.linea}, column {self.columna}")
        self.contador_errores += 1
        return None

    def escanear(self):
        """Función principal para escanear todo el archivo"""
        print("INFO SCAN - Start scanning…")
        token = self.obtener_token()
        while token is not None:
            self.tokens.append(token)  # Almacena el token en la lista
            token = self.obtener_token()
        print(f"INFO SCAN - Completed with {self.contador_errores} errors")