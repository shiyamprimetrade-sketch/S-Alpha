"""Bounded template-based software generation; no arbitrary source execution."""
import ast
import subprocess
import sys
from pathlib import Path
from .create import create

TEMPLATES = {
    "calculator": """def calculate(a, op, b):
    if op == '+': return a + b
    if op == '-': return a - b
    if op == '*': return a * b
    if op == '/': return a / b
    raise ValueError('unsupported operator')

if __name__ == '__main__':
    assert calculate(2, '+', 3) == 5
    assert calculate(7, '-', 2) == 5
    assert calculate(3, '*', 4) == 12
    assert calculate(8, '/', 2) == 4
    try:
        calculate(1, '/', 0)
    except ZeroDivisionError:
        pass
    else:
        raise AssertionError('division by zero')
    print('PASS')
""",
    "temperature": """def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

if __name__ == '__main__':
    assert celsius_to_fahrenheit(0) == 32
    assert celsius_to_fahrenheit(100) == 212
    assert celsius_to_fahrenheit(-40) == -40
    print('PASS')
"""
}

def build(kind, root):
    if kind not in TEMPLATES:
        raise ValueError("unsupported template")
    source = TEMPLATES[kind]
    ast.parse(source)
    # Execute only the built-in source, not a mutable workspace file.
    run = subprocess.run([sys.executable, "-I", "-c", source],
                         capture_output=True, text=True, timeout=10)
    if run.returncode or run.stdout.strip() != "PASS":
        raise RuntimeError("template self-test failed")
    artifact = create(root, kind + ".py", source)
    return {"kind": kind, "status": "verified", "artifact": artifact,
            "verification": "built-in source self-test"}

TEMPLATES["counter"] = """def count_words(text):
    return len(text.split())

if __name__ == '__main__':
    assert count_words('one two') == 2
    assert count_words('') == 0
    assert count_words('  one  ') == 1
    print('PASS')
"""
