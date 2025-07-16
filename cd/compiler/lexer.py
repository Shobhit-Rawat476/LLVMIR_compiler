class Token:
    def __init__(self, type, value, lineno):
        self.type = type
        self.value = value
        self.lineno = lineno
    
    def __str__(self):
        return f"Token({self.type}, {repr(self.value)}, line: {self.lineno})"
    
    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value,
            'line': self.lineno
        }

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
        self.lineno = 1
    
    def error(self):
        raise Exception(f"Invalid character '{self.current_char}' at line {self.lineno}")
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            if self.current_char == '\n':
                self.lineno += 1
            self.advance()
    
    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)
    
    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result
    
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char.isdigit():
                return Token('INTEGER', self.integer(), self.lineno)
            
            if self.current_char.isalpha() or self.current_char == '_':
                ident = self.identifier()
                if ident in ['int', 'return']:
                    return Token(ident.upper(), ident, self.lineno)
                return Token('ID', ident, self.lineno)
            
            if self.current_char == '=':
                self.advance()
                return Token('ASSIGN', '=', self.lineno)
            
            if self.current_char == ';':
                self.advance()
                return Token('SEMI', ';', self.lineno)
            
            if self.current_char == '(':
                self.advance()
                return Token('LPAREN', '(', self.lineno)
            
            if self.current_char == ')':
                self.advance()
                return Token('RPAREN', ')', self.lineno)
            
            if self.current_char == '{':
                self.advance()
                return Token('LBRACE', '{', self.lineno)
            
            if self.current_char == '}':
                self.advance()
                return Token('RBRACE', '}', self.lineno)
            
            if self.current_char == '*':
                self.advance()
                return Token('MUL', '*', self.lineno)
            
            self.error()
        
        return Token('EOF', None, self.lineno)
    
    def tokenize(self):
        tokens = []
        token = self.get_next_token()
        tokens.append(token)
        
        while token.type != 'EOF':
            token = self.get_next_token()
            tokens.append(token)
        
        return tokens[:-1]  # Exclude EOF token