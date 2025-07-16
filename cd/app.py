from flask import Flask, render_template, request, jsonify
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.irgen import IRGenerator
import os
from pygments import highlight
from pygments.lexers import LlvmLexer
from pygments.formatters import HtmlFormatter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                with open(filepath, 'r') as f:
                    source_code = f.read()
                return process_code(source_code)
        elif 'code' in request.form:
            return process_code(request.form['code'])
    
    return render_template('index.html')

def process_code(source_code):
    try:
        # Lexical Analysis
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Syntax Analysis
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Semantic Analysis
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        # IR Generation
        ir_gen = IRGenerator()
        ir_code = ir_gen.generate(ast)
        
        # Highlight LLVM IR
        highlighted_ir = highlight(ir_code, LlvmLexer(), HtmlFormatter())
        
        return jsonify({
            'success': True,
            'tokens': [str(tok) for tok in tokens],
            'ast': ast.to_dict(),
            'symbol_table': analyzer.symbol_table,
            'ir': ir_code,
            'highlighted_ir': highlighted_ir
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)