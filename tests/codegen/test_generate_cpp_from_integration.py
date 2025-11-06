import textwrap
from pathlib import Path


def test_generate_cpp_from_integration_sample(tmp_path):
    """Integration-style test: parse a sample .flpy (lexer/parser output)
    and run Persona 3 ProgramGenerator to emit a C++ file. This test
    only verifies that generation succeeds and produces a plausible C++
    file (no compilation).

    Note: Persona 3 generator may rely on provisional Persona 2/Persona 1
    helpers. The generated C++ will include a temporary DynamicValue stub
    when using the project's ProgramGenerator.
    """

    sample = textwrap.dedent('''
    def hola(a,b):
        return a + b

    print(hola(1,2))

    def fib(n):
        if n == 1 or n == 2:
            return 1
        else:
            return fib(n-1) + fib(n-2)
    print (fib(5))


    a = 4
    print(a)
    b = 5
    a = "hola"
    b = a + (str(b))
    print(b)

    a = [1, "hola", {"z": 1, "x": "ECCI"}, [1,2,3,4], (1,2,3,4)]
    print(a)
    print("Fibonacci")

    for i in range(len(a)-1):
        print(a[i])
        
    for e in a[3]:
        print (e)
        
    a=5
    b=10
    while a < b:
        print(fib(b-5))
        c = b
        b = "hola"
        b=c-2
    print("Si printeo mis probabilidades de graduarme suben :)")
    ''')

    # Write sample to a temporary file (simulates lexer output)
    src_file = tmp_path / 'integration_sample.flpy'
    src_file.write_text(sample)

    # Import project parser and program generator
    import sys
    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root))

    from src.parser.parser import Parser
    from src.codegen.program_generator import ProgramGenerator

    text = src_file.read_text()
    parser = Parser()
    module = parser.parse(text)

    statements = getattr(module, 'body', module)

    pg = ProgramGenerator()
    cpp = pg.generate_cpp(statements)

    out_file = tmp_path / 'generated_program.cpp'
    out_file.write_text(cpp)

    # Basic assertions: file exists and contains expected markers
    assert out_file.exists()
    content = out_file.read_text()
    assert 'int main()' in content
    # The Persona 3 generator currently emits a DynamicValue stub for testing
    assert 'DynamicValue' in content
    # Ensure function names from the sample appear in the generated output
    assert 'hola' in content
    assert 'fib' in content