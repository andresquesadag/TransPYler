# src/tools/transpile_cli.py
import argparse
from src.compiler.transpiler import Transpiler

def main():
    p = argparse.ArgumentParser(description="Transpile Fangless Python to C++")
    p.add_argument("input", help="Input .flpy/.py file")
    p.add_argument("-o", "--output", default="output.cpp", help="Output C++ file")
    args = p.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        source = f.read()

    t = Transpiler()
    out = t.transpile(source, filename=args.output)
    print(f"[ok] C++ generado en: {out}")

if __name__ == "__main__":
    main()
