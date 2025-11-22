# ============================================================================
# TransPYler - Makefile
# ============================================================================
# Makefile for transpiling, compiling, and executing Fangless Python code
#
# Usage:
#   make transpile    - Only transpile to C++
#   make compile      - Transpile and compile to executable
#   make run          - Transpile, compile, and execute
#   make clean        - Clean generated files
#   make help         - Show this help
#
# Requirements:
#   - Python 3.x
#   - g++ compiler (via MSYS2/MinGW on Windows)
#   - make (via MSYS2 on Windows, pre-installed on Linux/Mac)
# ============================================================================

# Force use of sh shell (works on Windows with MSYS2, Linux, and macOS)
SHELL := /bin/sh

# Configuration variables
PYTHON = python
TRANSPILER = src.tools.transpile_cli
INPUT_FILE = examples/profe_full_feature_test.py
OUTPUT_DIR = build
CPP_FILE = $(OUTPUT_DIR)/profe_full_feature_test.cpp
EXE_FILE = $(OUTPUT_DIR)/profe_full_feature_test.exe
RUNTIME_DIR = src/runtime/cpp

# C++ Compiler
CXX = g++
CXXFLAGS = -std=c++17 -Wall -I$(RUNTIME_DIR)
RUNTIME_SOURCES = $(RUNTIME_DIR)/DynamicType.cpp $(RUNTIME_DIR)/builtins.cpp

# Colors for output (ANSI escape codes work in most terminals)
GREEN = \033[32m
YELLOW = \033[33m
BLUE = \033[36m
RED = \033[31m
RESET = \033[0m

# ============================================================================
# Main rules
# ============================================================================

.PHONY: all help transpile compile run clean status

# Default rule
all: help

# Help
help:
	@printf "============================================================================\n"
	@printf " TransPYler - Python to C++ Transpilation System\n"
	@printf "============================================================================\n"
	@printf "\n"
	@printf "Available targets:\n"
	@printf "  make transpile    - Only transpile to C++ (generates $(CPP_FILE))\n"
	@printf "  make compile      - Transpile and compile (generates $(EXE_FILE))\n"
	@printf "  make run          - Transpile, compile, and execute the program\n"
	@printf "  make clean        - Remove generated files in $(OUTPUT_DIR)/\n"
	@printf "  make help         - Show this help\n"
	@printf "\n"
	@printf "Input file: $(INPUT_FILE)\n"
	@printf "============================================================================\n"

# Target 1: Only transpile
transpile: $(OUTPUT_DIR)
	@printf "$(BLUE)[1/1] Transpiling $(INPUT_FILE) to C++...$(RESET)\n"
	$(PYTHON) -m $(TRANSPILER) $(INPUT_FILE) -o $(CPP_FILE)
	@printf "$(GREEN)[OK] Transpilation complete: $(CPP_FILE)$(RESET)\n"

# Target 2: Transpile and compile
compile: transpile
	@printf "$(BLUE)[2/2] Compiling $(CPP_FILE) to executable...$(RESET)\n"
	$(CXX) $(CXXFLAGS) $(CPP_FILE) $(RUNTIME_SOURCES) -o $(EXE_FILE)
	@printf "$(GREEN)[OK] Compilation complete: $(EXE_FILE)$(RESET)\n"

# Target 3: Transpile, compile, and execute
run: compile
	@printf "$(BLUE)[3/3] Executing $(EXE_FILE)...$(RESET)\n"
	@printf "$(YELLOW)============ Program Output ============$(RESET)\n"
	@./$(EXE_FILE)
	@printf "$(YELLOW)========================================$(RESET)\n"
	@printf "$(GREEN)[OK] Execution completed successfully$(RESET)\n"

# Create output directory if it doesn't exist
$(OUTPUT_DIR):
	@mkdir -p $(OUTPUT_DIR)

# Clean generated files
clean:
	@printf "$(YELLOW)Cleaning generated files...$(RESET)\n"
	@rm -f $(OUTPUT_DIR)/*.cpp $(OUTPUT_DIR)/*.exe $(OUTPUT_DIR)/*.o
	@printf "$(GREEN)[OK] Cleanup complete$(RESET)\n"

# Status information
status:
	@printf "TransPYler project status:\n"
	@printf "  Input file: $(INPUT_FILE)\n"
	@printf "  Generated C++ file: $(CPP_FILE)\n"
	@printf "  Executable: $(EXE_FILE)\n"
	@printf "\n"
	@test -f $(CPP_FILE) && printf "  $(GREEN)[OK] C++ file exists$(RESET)\n" || printf "  $(YELLOW)[--] C++ file doesn't exist (run 'make transpile')$(RESET)\n"
	@test -f $(EXE_FILE) && printf "  $(GREEN)[OK] Executable exists$(RESET)\n" || printf "  $(YELLOW)[--] Executable doesn't exist (run 'make compile')$(RESET)\n"
