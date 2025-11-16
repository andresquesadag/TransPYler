# Smoke test for C++ code generation David

import sys
import os

# Add the project root to sys.path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.codegen.code_generator_cpp import CodeGeneratorCpp
from src.core import Module, FunctionDef, Identifier, BinaryExpr, UnaryExpr, LiteralExpr, CallExpr
from src.core import Assign, ExprStmt, Return

# Use the C++ oriented generator which creates a full .cpp file (preamble + functions + main)
cg = CodeGeneratorCpp()

# 1) Function: add(a,b)
fn_add = FunctionDef(
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

# 2) Function: power(a,b) -> uses ** to map to builtins::pow
fn_pow = FunctionDef(
    name="power",
    params=[Identifier(name="a"), Identifier(name="b")],
    body=[
        Assign(
            target=Identifier(name="res"),
            value=BinaryExpr(left=Identifier(name="a"), op="**", right=Identifier(name="b"))
        ),
        Return(value=Identifier(name="res"))
    ]
)

# 3) Function: unary_test(a) -> demonstrates unary -
fn_unary = FunctionDef(
    name="unary_test",
    params=[Identifier(name="a")],
    body=[
        Assign(
            target=Identifier(name="b"),
            value=UnaryExpr(op='-', operand=Identifier(name="a"))
        ),
        Return(value=Identifier(name="b"))
    ]
)

# 4) Function: call_test() -> calls add(1,2)
fn_call = FunctionDef(
    name="call_test",
    params=[],
    body=[
        Return(value=CallExpr(callee=Identifier(name="add"), args=[LiteralExpr(1), LiteralExpr(2)]))
    ]
)

# Global statements to appear in main(): declare and reassign
global_assign1 = Assign(target=Identifier(name="g"), value=LiteralExpr(10))
global_reassign = Assign(target=Identifier(name="g"), value=BinaryExpr(left=Identifier(name="g"), op="+", right=LiteralExpr(5)))

# Build module with functions and globals
module = Module(body=[fn_add, fn_pow, fn_unary, fn_call, global_assign1, global_reassign])

out_file = 'resultado_codegen_cpp_smoke.cpp'
code = cg.generate(module)

# write the file
with open(out_file, 'w', encoding='utf-8') as f:
    f.write(code)

print('WROTE', out_file)

# Simple textual checks to validate the features
checks = [
    ("_fn_add(", "function 'add' header"),
    ("builtins::pow(", "pow mapping for '**'"),
    ("DynamicType x", "assignment inside function 'add'"),
    ("DynamicType g = DynamicType(10)", "global first declaration of g"),
    ("g = ", "global reassignment of g"),
    ("_fn_add(", "call translation to _fn_add"),
    ("DynamicType b =", "unary assignment in unary_test"),
]

failed = []
for substr, desc in checks:
    if substr not in code:
        failed.append((substr, desc))

if failed:
    print('\nFAILED checks:')
    for s, d in failed:
        print(f" - missing '{s}'  ({d})")
    sys.exit(2)

print('\nAll codegen_cpp_smoke checks passed.')
