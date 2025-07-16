from llvmlite import ir

class IRGenerator:
    def __init__(self):
        self.module = ir.Module(name='main_module')
        self.builder = None
        self.symbol_table = {}
    
    def generate(self, node):
        if node.type == 'FUNCTION':
            return self.generate_function(node)
    
    def generate_function(self, node):
        func_name = node.children[0].value
        
        # Create function type (returns int32, takes no args)
        func_type = ir.FunctionType(ir.IntType(32), [])
        
        # Create function
        function = ir.Function(self.module, func_type, name=func_name)
        
        # Create entry block
        entry_block = function.append_basic_block(name='entry')
        self.builder = ir.IRBuilder(entry_block)
        
        # Process declarations
        declarations = node.children[1]
        for decl in declarations.children:
            self.generate_declaration(decl)
        
        # Process statements
        statements = node.children[2]
        for stmt in statements.children:
            self.generate_statement(stmt)
        
        # Add default return if missing
        if not statements.children or statements.children[-1].type != 'RETURN':
            self.builder.ret(ir.Constant(ir.IntType(32), 0))
        
        return str(self.module)
    
    def generate_declaration(self, node):
        var_name = node.children[0].value
        
        # Allocate memory for the variable
        ptr = self.builder.alloca(ir.IntType(32), name=var_name)
        self.symbol_table[var_name] = ptr
        
        # If there's an initial value
        if len(node.children) > 1:
            value = self.generate_expression(node.children[1])
            self.builder.store(value, ptr)
    
    def generate_statement(self, node):
        if node.type == 'RETURN':
            value = self.generate_expression(node.children[0])
            self.builder.ret(value)
        elif node.type == 'ASSIGNMENT':
            var_name = node.children[0].value
            ptr = self.symbol_table[var_name]
            value = self.generate_expression(node.children[1])
            self.builder.store(value, ptr)
    
    def generate_expression(self, node):
        if node.type == 'INTEGER':
            return ir.Constant(ir.IntType(32), node.value)
        elif node.type == 'ID':
            ptr = self.symbol_table[node.value]
            return self.builder.load(ptr, name=node.value)
        elif node.type == 'BINOP':
            left = self.generate_expression(node.children[0])
            right = self.generate_expression(node.children[1])
            
            if node.value == '+':
                return self.builder.add(left, right, name='addtmp')
            elif node.value == '-':
                return self.builder.sub(left, right, name='subtmp')
            elif node.value == '*':
                return self.builder.mul(left, right, name='multmp')
            elif node.value == '/':
                return self.builder.sdiv(left, right, name='divtmp')