from src.codegen.code_generator_cpp import CodeGeneratorCpp
from src.core import Module
from src.core.ast.ast_definitions import FunctionDef
from src.core.ast.ast_expressions import Identifier, BinaryExpr
from src.core.ast.ast_statements import Return, Assign

# Use the C++ oriented generator which creates a full .cpp file (preamble + functions + main)
cg = CodeGeneratorCpp()

# AST: def add(a, b): x = a + b; return x
fn = FunctionDef(
    name="add",
    params=[Identifier(name="a"), Identifier(name="b")],
    body=[
        Assign(
            target=Identifier(name="x"),
            value=BinaryExpr(left=Identifier(name="a"), op="+", right=Identifier(name="b"))
        ),
        Return(value=Identifier(name="x"))
    ]
)

# Wrap into a Module so CodeGeneratorCpp.generate can produce preamble + functions + main
module = Module(body=[fn])

out_file = 'pruebaPersona2.cpp'
code = cg.generate(module)
with open(out_file, 'w', encoding='utf-8') as f:
    f.write(code)

print('WROTE', out_file)
