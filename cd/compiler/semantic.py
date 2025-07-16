class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
    
    def analyze(self, node):
        if node.type == 'FUNCTION':
            self.visit_function(node)
    
    def visit_function(self, node):
        # Process declarations
        declarations = node.children[1]
        for decl in declarations.children:
            self.visit_declaration(decl)
        
        # Process statements
        statements = node.children[2]
        for stmt in statements.children:
            self.visit_statement(stmt)
    
    def visit_declaration(self, node):
        var_name = node.children[0].value
        if var_name in self.symbol_table:
            raise Exception(f"Duplicate declaration of variable '{var_name}'")
        
        self.symbol_table[var_name] = 'int'
        
        if len(node.children) > 1:  # Has initialization
            self.visit_expression(node.children[1])
    
    def visit_statement(self, node):
        if node.type == 'RETURN':
            self.visit_expression(node.children[0])
        elif node.type == 'ASSIGNMENT':
            var_name = node.children[0].value
            if var_name not in self.symbol_table:
                raise Exception(f"Undeclared variable '{var_name}'")
            self.visit_expression(node.children[1])
    
    def visit_expression(self, node):
        if node.type == 'ID':
            var_name = node.value
            if var_name not in self.symbol_table:
                raise Exception(f"Undeclared variable '{var_name}'")
        elif node.type == 'BINOP':
            self.visit_expression(node.children[0])
            self.visit_expression(node.children[1])