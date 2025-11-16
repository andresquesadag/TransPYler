
# NOTA: Lo hice como un Auxiliar para no travesear aun el code_generator.py

from typing import List
from src.core import (
    AstNode, Module, FunctionDef, Block, If, While, For,
    Assign, ExprStmt, Return
)
from .scope_manager import ScopeManager
from .expr_generator import ExprGenerator
from .basic_statement_generator import BasicStatementGenerator
from .function_generator import FunctionGenerator
from .statement_generator import StatementVisitor  # Persona 3

CPP_PREAMBLE = """#include <iostream>
#include <string>
#include "dynamic_type.hpp"
#include "builtins.hpp"
using namespace std;
"""

class CodeGeneratorCpp:
    def __init__(self):
        self.scope = ScopeManager()
        self.expr_gen   = ExprGenerator(scope=self.scope)           # Persona 2
        self.basic_stmt = BasicStatementGenerator(scope=self.scope) # Persona 2
        self.ctrl_stmt  = StatementVisitor(target="cpp")            # Persona 3
        self.func_gen   = FunctionGenerator(scope=self.scope)       # Persona 2

    def generate(self, module: Module) -> str:
        if not isinstance(module, Module):
            raise TypeError("CodeGeneratorCpp.generate espera un nodo Module")

        self.scope.reset()

        # 1) separar funciones del resto
        fun_defs: List[FunctionDef] = [n for n in module.body if isinstance(n, FunctionDef)]
        globals_: List[AstNode]     = [n for n in module.body if not isinstance(n, FunctionDef)]

        parts: List[str] = [CPP_PREAMBLE]

        # 2) funciones primero
        for f in fun_defs:
            parts.append(self.func_gen.visit(f))
            parts.append("")

        # 3) global en main()
        parts.append("int main() {")
        self.scope.push()
        for stmt in globals_:
            parts.extend(self._emit_top_stmt(stmt))
        self.scope.pop()
        parts.append("  return 0;")
        parts.append("}")

        return "\n".join(parts)

    def _emit_top_stmt(self, stmt: AstNode) -> List[str]:
        # statements básicos (tu parte)
        if isinstance(stmt, (Assign, ExprStmt, Return)):
            return ["  " + self.basic_stmt.visit(stmt)]
        # control de flujo (Persona 3)
        if isinstance(stmt, (If, While, For, Block)):
            block_code = self.ctrl_stmt.visit(stmt)
            return ["  " + line if line.strip() else line
                    for line in block_code.splitlines()]
        raise NotImplementedError(f"[CodeGeneratorCpp] Statement no soportado en global: {type(stmt).__name__}")
