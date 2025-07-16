from compiler.lexer import Token

class ASTNode:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children or []
        self.value = value
    
    def __str__(self):
        return self.to_string()
    
    def to_string(self, level=0):
        ret = "  " * level + f"{self.type}"
        if self.value is not None:
            ret += f": {self.value}"
        ret += "\n"
        for child in self.children:
            ret += child.to_string(level + 1)
        return ret
    
    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value,
            'children': [child.to_dict() for child in self.children]
        }

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = self.tokens[0] if self.tokens else None
        self.pos = 0
    
    def error(self):
        raise Exception('Invalid syntax')
    
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = None
        else:
            self.error()
    
    def parse(self):
        node = self.program()
        if self.current_token is not None:
            self.error()
        return node
    
    def program(self):
        return self.function_declaration()
    
    def function_declaration(self):
        self.eat('INT')
        func_name = self.current_token.value
        self.eat('ID')
        self.eat('LPAREN')
        self.eat('RPAREN')
        self.eat('LBRACE')
        
        declarations = []
        statements = []
        
        while self.current_token and self.current_token.type == 'INT':
            declarations.append(self.variable_declaration())
        
        while self.current_token and self.current_token.type != 'RBRACE':
            statements.append(self.statement())
        
        self.eat('RBRACE')
        
        return ASTNode('FUNCTION', [
            ASTNode('NAME', value=func_name),
            ASTNode('DECLARATIONS', declarations),
            ASTNode('STATEMENTS', statements)
        ])
    
    def variable_declaration(self):
        self.eat('INT')
        var_name = self.current_token.value
        self.eat('ID')
        
        if self.current_token and self.current_token.type == 'ASSIGN':
            self.eat('ASSIGN')
            expr = self.expr()
            self.eat('SEMI')
            return ASTNode('DECLARATION', [
                ASTNode('ID', value=var_name),
                expr
            ])
        else:
            self.eat('SEMI')
            return ASTNode('DECLARATION', [
                ASTNode('ID', value=var_name)
            ])
    
    def statement(self):
        if self.current_token.type == 'RETURN':
            return self.return_statement()
        elif self.current_token.type == 'ID':
            return self.assignment_statement()
        else:
            self.error()
    
    def return_statement(self):
        self.eat('RETURN')
        expr = self.expr()
        self.eat('SEMI')
        return ASTNode('RETURN', [expr])
    
    def assignment_statement(self):
        var_name = self.current_token.value
        self.eat('ID')
        self.eat('ASSIGN')
        expr = self.expr()
        self.eat('SEMI')
        return ASTNode('ASSIGNMENT', [
            ASTNode('ID', value=var_name),
            expr
        ])
    
    def expr(self):
        node = self.term()
        
        while self.current_token and self.current_token.type in ('PLUS', 'MINUS'):
            token = self.current_token
            if token.type == 'PLUS':
                self.eat('PLUS')
            elif token.type == 'MINUS':
                self.eat('MINUS')
            
            node = ASTNode('BINOP', [
                node,
                self.term()
            ], value=token.value)
        
        return node
    
    def term(self):
        node = self.factor()
        
        while self.current_token and self.current_token.type in ('MUL', 'DIV'):
            token = self.current_token
            if token.type == 'MUL':
                self.eat('MUL')
            elif token.type == 'DIV':
                self.eat('DIV')
            
            node = ASTNode('BINOP', [
                node,
                self.factor()
            ], value=token.value)
        
        return node
    
    def factor(self):
        token = self.current_token
        if token.type == 'INTEGER':
            self.eat('INTEGER')
            return ASTNode('INTEGER', value=token.value)
        elif token.type == 'ID':
            self.eat('ID')
            return ASTNode('ID', value=token.value)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        else:
            self.error()