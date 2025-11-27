# 6.4 Code Generation Architecture

The code generation system is built on a modular architecture with specialized generators:

## DynamicType System

The `DynamicType` class is the core of Python-to-C++ type emulation:

- **Runtime Type Storage**: Uses `std::variant` to hold values of different types
- **Type Enumeration**: Tracks current type (INT, DOUBLE, STRING, BOOL, NONE, LIST, DICT, SET)
- **Automatic Conversions**: Methods like `toInt()`, `toDouble()`, `toString()`, `toBool()`
- **Operator Overloading**: All Python operators (+, -, \*, /, %, //, \*\*, ==, !=, <, >, etc.)
- **Collection Support**: Native support for lists, dictionaries, and sets
- **Method Support**: Methods like `append()`, `get()`, `remove()`, `add()`

## Code Generators

1. **ExprGenerator** (`expr_generator.py`)

   - Handles literals, identifiers, operators
   - Binary and unary expression translation
   - Function call generation
   - Attribute access and subscripting

2. **StatementGenerator** (`statement_generator.py`)

   - Control flow: if/elif/else, while, for
   - Break, continue, pass statements
   - Proper indentation and formatting

3. **BasicStatementGenerator** (`basic_statement_generator.py`)

   - Variable assignments (simple and augmented)
   - Expression statements
   - Return statements
   - Automatic variable declaration

4. **FunctionGenerator** (`function_generator.py`)

   - Function definition translation
   - Parameter handling
   - Scope management
   - Return type handling

5. **DataStructureGenerator** (`data_structure_generator.py`)

   - List, tuple, set, dictionary literals
   - Type deduction for C++ containers
   - Nested structure support

6. **CodeGenerator** (`code_generator.py`)
   - Main orchestrator
   - Integrates all generators
   - Manages file output
   - Adds necessary includes
