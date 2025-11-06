"""
Unit Tests for Control Flow Code Generator
Person 3 - Testing Suite

Tests all control flow structures:
- if/elif/else
- while loops (including while-else)
- for loops (including for-else and range optimization)
- break/continue/pass/return
- Nested structures
- Edge cases
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from codegen.control_flow_generator import ControlFlowGenerator
from codegen._stubs import StubExpressionGenerator


class MockNode:
    """Mock AST node for testing"""
    def __init__(self, node_type, **kwargs):
        # Store the declared node type on the instance rather than mutating
        # the class __name__ (mutating the class breaks other instances).
        self.node_type = node_type
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_simple_if():
    """Test simple if statement generation"""
    print("Test: Simple If Statement")
    
    gen = ControlFlowGenerator(StubExpressionGenerator())
    
    # Create mock AST: if x > 5: pass
    condition = MockNode('Compare',
        left=MockNode('Name', id='x'),
        ops=[MockNode('Gt')],
        comparators=[MockNode('Constant', value=5)]
    )
    
    if_node = MockNode('If',
        test=condition,
        body=[MockNode('Pass')],
        orelse=[]
    )

    print("DEBUG If node attributes:", dir(if_node))
    
    gen.visit(if_node)
    code = gen.get_code()
    
    print(code)
    assert 'if' in code
    assert 'toBool()' in code
    print("✓ Passed\n")


def test_if_elif_else():
    """Test if/elif/else chain"""
    print("Test: If/Elif/Else Chain")
    
    gen = ControlFlowGenerator(StubExpressionGenerator())
    
    # if x > 10: pass
    # elif x > 5: pass
    # else: pass
    
    elif_node = MockNode('If',
        test=MockNode('Compare',
            left=MockNode('Name', id='x'),
            ops=[MockNode('Gt')],
            comparators=[MockNode('Constant', value=5)]
        ),
        body=[MockNode('Pass')],
        orelse=[MockNode('Pass')]
    )
    
    if_node = MockNode('If',
        test=MockNode('Compare',
            left=MockNode('Name', id='x'),
            ops=[MockNode('Gt')],
            comparators=[MockNode('Constant', value=10)]
        ),
        body=[MockNode('Pass')],
        orelse=[elif_node]
    )
    
    gen.visit(if_node)
    code = gen.get_code()
    
    print(code)
    assert 'if' in code
    assert 'else if' in code or 'else' in code
    print("✓ Passed\n")


def test_while_loop():
    """Test while loop generation"""
    print("Test: While Loop")
    
    gen = ControlFlowGenerator(StubExpressionGenerator())
    
    # while x > 0: pass
    while_node = MockNode('While',
        test=MockNode('Compare',
            left=MockNode('Name', id='x'),
            ops=[MockNode('Gt')],
            comparators=[MockNode('Constant', value=0)]
        ),
        body=[MockNode('Pass')],
        orelse=[]
    )
    
    gen.visit(while_node)
    code = gen.get_code()
    
    print(code)
    assert 'while' in code
    assert 'toBool()' in code
    print("✓ Passed\n")


def test_while_else():
    """Test while-else construct"""
    print("Test: While-Else")
    
    gen = ControlFlowGenerator(StubExpressionGenerator())
    
    # while x > 0:
    #     pass
    # else:
    #     pass
    
    while_node = MockNode('While',
        test=MockNode('Compare',
            left=MockNode('Name', id='x'),
            ops=[MockNode('Gt')],
            comparators=[MockNode('Constant', value=0)]
        ),
        body=[MockNode('Pass')],
        orelse=[MockNode('Pass')]
    )
    
    gen.visit(while_node)
    code = gen.get_code()
    
    print(code)
    assert 'while' in code
    assert '_while_completed' in code
    assert 'if' in code  # For the else clause check
    print("✓ Passed\n")


def test_for_range():
    """Test for loop with range()"""
    print("Test: For Loop with range()")
    
    gen = ControlFlowGenerator(StubExpressionGenerator())
    
    # for i in range(10): pass
    range_call = MockNode('Call',
        func=MockNode('Name', id='range'),
        args=[MockNode('Constant', value=10)],
        keywords=[]
    )
    
    for_node = MockNode('For',
        target=MockNode('Name', id='i'),
        iter=range_call,
        body=[MockNode('Pass')],
        orelse=[]
    )
    
    gen.visit(for_node)
    code = gen.get_code()
    
    print(code)
    assert 'for' in code
    assert 'int i' in code  # Optimized integer loop
    print("✓ Passed\n")


def test_break_continue():
    """Test break and continue statements"""
    print("Test: Break and Continue")
    
    gen = ControlFlowGenerator(StubExpressionGenerator())
    
    # while True:
    #     break
    #     continue
    
    while_node = MockNode('While',
        test=MockNode('NameConstant', value=True),
        body=[
            MockNode('Break'),
            MockNode('Continue')
        ],
        orelse=[]
    )
    
    gen.visit(while_node)
    code = gen.get_code()
    
    print(code)
    assert 'break;' in code
    assert 'continue;' in code
    print("✓ Passed\n")


def test_break_outside_loop_error():
    """Test that break outside loop raises error"""
    print("Test: Break Outside Loop (Should Error)")
    
    gen = ControlFlowGenerator(StubExpressionGenerator())
    
    break_node = MockNode('Break')
    
    try:
        gen.visit(break_node)
        print("✗ Failed: Should have raised SyntaxError")
    except SyntaxError as e:
        print(f"✓ Passed: Correctly raised SyntaxError: {e}\n")


def test_nested_loops():
    """Test nested loop structures"""
    print("Test: Nested Loops")
    
    gen = ControlFlowGenerator(StubExpressionGenerator())
    
    # for i in range(3):
    #     for j in range(3):
    #         pass
    
    inner_for = MockNode('For',
        target=MockNode('Name', id='j'),
        iter=MockNode('Call',
            func=MockNode('Name', id='range'),
            args=[MockNode('Constant', value=3)],
            keywords=[]
        ),
        body=[MockNode('Pass')],
        orelse=[]
    )
    
    outer_for = MockNode('For',
        target=MockNode('Name', id='i'),
        iter=MockNode('Call',
            func=MockNode('Name', id='range'),
            args=[MockNode('Constant', value=3)],
            keywords=[]
        ),
        body=[inner_for],
        orelse=[]
    )
    
    gen.visit(outer_for)
    code = gen.get_code()
    
    print(code)
    assert code.count('for') == 2  # Two for loops
    print("✓ Passed\n")


def test_return_statement():
    """Test return statement generation"""
    print("Test: Return Statement")
    
    gen = ControlFlowGenerator(StubExpressionGenerator())
    
    # return 42
    return_node = MockNode('Return',
        value=MockNode('Constant', value=42)
    )
    
    gen.visit(return_node)
    code = gen.get_code()
    
    print(code)
    assert 'return' in code
    assert '42' in code
    print("✓ Passed\n")


def run_all_tests():
    """Run all test cases"""
    print("=" * 60)
    print("Running Control Flow Generator Tests")
    print("=" * 60 + "\n")
    
    test_simple_if()
    test_if_elif_else()
    test_while_loop()
    test_while_else()
    test_for_range()
    test_break_continue()
    test_break_outside_loop_error()
    test_nested_loops()
    test_return_statement()
    
    print("=" * 60)
    print("All Tests Completed!")
    print("=" * 60)


if __name__ == '__main__':
    run_all_tests()

