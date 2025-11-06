#!/usr/bin/env python3
"""Small helper: parse a .flpy file with the project's parser and generate C++.

This script is a convenience tool to validate that the code generators accept
AST nodes produced by the real parser. It writes the generated C++ to
out/generated_program.cpp and a provisional dynamic value stub to
out/dynamic_value_stub.hpp, then attempts to compile with g++.

Usage:
  python3 src/tools/generate_from_parser.py [input.flpy]

Note: This is a lightweight, provisional helper for Persona 3 testing.
"""
import sys
import os
from pathlib import Path
import subprocess
import argparse

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

# Ensure the project src is on sys.path so imports like `src.parser` work
sys.path.insert(0, str(ROOT))

parser_arg = argparse.ArgumentParser(description="Parse a .flpy file and generate C++.")
parser_arg.add_argument("input", nargs="?", default="tests/lexer/Integration_test_1.flpy", help="Input .flpy file")
parser_arg.add_argument("--call", dest="call", help="Optional: call a function after generation, format name:arg (e.g. fibonacci:6)")
parser_arg.add_argument("--compile", dest="compile", action='store_true', help="If set, compile and run the generated C++ (off by default)")
args = parser_arg.parse_args()

infile = ROOT / args.input
if not infile.exists():
  print(f"Input file not found: {infile}")
  sys.exit(2)

text = infile.read_text()

from src.parser.parser import Parser
from src.codegen.program_generator import ProgramGenerator
from src.codegen._stubs import get_stub_dynamic_value_class

parser = Parser()
module = parser.parse(text)

statements = getattr(module, "body", module)

# If requested, append a call statement to the parsed AST so the generated
# program will call the function and produce visible behavior.
if args.call:
  try:
    fname, farg = args.call.split(":", 1)
  except ValueError:
    print("--call expects format name:arg, e.g. fibonacci:6")
    sys.exit(2)

  # Import AST node classes to construct a call expression
  from src.core.ast.ast_expressions import CallExpr, Identifier, LiteralExpr
  from src.core.ast.ast_statements import ExprStmt

  call = CallExpr(callee=Identifier(name=fname), args=[LiteralExpr(value=int(farg))])
  call_stmt = ExprStmt(value=call)

  # Append to module body (works whether module is a Module wrapper or a list)
  if hasattr(module, 'body'):
    module.body.append(call_stmt)
    statements = module.body
  elif isinstance(statements, list):
    statements.append(call_stmt)

pg = ProgramGenerator()
cpp = pg.generate_cpp(statements)

stub = get_stub_dynamic_value_class()

cpp_file = OUT / "generated_program.cpp"
stub_file = OUT / "dynamic_value_stub.hpp"

stub_file.write_text(stub)
cpp_file.write_text(cpp)

print(f"Wrote: {cpp_file}\nWrote: {stub_file}")

exe = OUT / "generated_program"
if args.compile:
    cmd = ["g++", "-std=c++17", "-O2", str(cpp_file), "-o", str(exe)]
    print("Compiling:", " ".join(cmd))
    proc = subprocess.run(cmd)
    print("g++ return code:", proc.returncode)
    if proc.returncode == 0:
        print("Binary created:", exe)
        # If compilation succeeded and user requested, run it to show output
        run_proc = subprocess.run([str(exe)])
        print("Program exit code:", run_proc.returncode)
else:
    print("Skipping compilation (pass --compile to build). Generated only.")
