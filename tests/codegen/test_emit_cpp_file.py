"""Generate a compilable C++ file using the control-flow generator and compile it.

This test is intentionally simple: it generates a small C++ program that
declares a DynamicValue, generates an `if` using the ControlFlowGenerator
and the StubExpressionGenerator, writes the .cpp file, then invokes g++ to
compile it. The goal is to verify the emitted code is syntactically valid
and can be compiled as a standalone program.
"""

import os
import sys
import subprocess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codegen.control_flow_generator import ControlFlowGenerator
from codegen._stubs import StubExpressionGenerator, get_stub_dynamic_value_class


def test_emit_and_compile_cpp():
    # Build a simple AST using real project AST nodes: if x > 5: pass
    from core.ast.ast_expressions import ComparisonExpr, Identifier, LiteralExpr
    from core.ast.ast_statements import If, Block, Pass

    condition = ComparisonExpr(left=Identifier(name='x'), op='Gt', right=LiteralExpr(value=5))
    if_node = If(cond=condition, body=Block(statements=[Pass()]), elifs=[], orelse=None)

    # Use the real expression generator which now understands core AST nodes
    from codegen.expr_generator import ExpressionGenerator
    gen = ControlFlowGenerator(ExpressionGenerator())
    gen.visit(if_node)
    body_code = gen.get_code()

    # Compose a full C++ file: includes, stub DynamicValue, and main()
    includes = """
#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <stdexcept>
"""

    stub_class = get_stub_dynamic_value_class()
    # Make dict printing deterministic for tests by using std::map instead
    # of unordered_map in the stub. Write the stub into a header that the
    # generated .cpp will include.
    stub_class = stub_class.replace('#include <unordered_map>', '#include <map>')
    stub_class = stub_class.replace('std::unordered_map', 'std::map')

    main_code = f"""
int main() {{
    // Example variable used by generated code
    DynamicValue x(10);

{body_code}
    return 0;
}}
"""

    out_dir = os.path.join(os.path.dirname(__file__), 'out')
    os.makedirs(out_dir, exist_ok=True)

    # Write header with the stub class so the generated .cpp can include it.
    header_path = os.path.join(out_dir, 'dynamic_value_stub.hpp')
    with open(header_path, 'w') as hf:
        hf.write(stub_class)

    full_cpp = includes + '\n' + '#include "dynamic_value_stub.hpp"' + "\n" + main_code
    cpp_path = os.path.join(out_dir, 'generated_program.cpp')
    exe_path = os.path.join(out_dir, 'generated_program')

    with open(cpp_path, 'w') as f:
        f.write(full_cpp)

    # Try to compile using g++
    compile_cmd = ['g++', '-std=c++17', '-O2', cpp_path, '-o', exe_path]
    print('Compiling:', ' '.join(compile_cmd))
    proc = subprocess.run(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    print('g++ return code:', proc.returncode)
    if proc.stdout:
        print('g++ stdout:\n', proc.stdout)
    if proc.stderr:
        print('g++ stderr:\n', proc.stderr)

    assert proc.returncode == 0, f"Compilation failed: {proc.stderr}"


if __name__ == '__main__':
    test_emit_and_compile_cpp()
