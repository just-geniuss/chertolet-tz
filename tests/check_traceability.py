"""Статическая проверка кейсов без импорта отсутствующей реализации транспорта."""
import ast
import re
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    source = ast.parse((root / 'tests/test_chertolet.py').read_text(encoding='utf-8'))
    document = (root / 'TEST_CASES.md').read_text(encoding='utf-8')
    spec = (root / 'SPEC.md').read_text(encoding='utf-8')
    methods = [node for node in ast.walk(source)
               if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
    expected = {f'TC-M-{i:03}' for i in range(1, 25)} | {f'TC-S-{i:03}' for i in range(1, 6)}
    actual = set()
    for method in methods:
        case = re.match(r'test_(TC_[MS]_\d{3})_', method.name).group(1).replace('_', '-')
        assert case in (ast.get_docstring(method) or ''), (method.name, 'missing docstring ID')
        assert re.search(rf'^\| {case} \|.*\b{method.name}\b', document, re.M), method.name
        actual.add(case)
    assert actual == expected and len(methods) == len(expected), 'case IDs differ'
    table_rows = re.findall(r'^\| (TC-[MS]-\d{3}) \|', document, re.M)
    assert len(table_rows) == len(expected) and set(table_rows) == expected
    requirements = {f'R{i:02}' for i in range(1, 17)}
    matrix = dict(re.findall(r'^\| (R\d{2}) \| ([^\n]+) \|$', document, re.M))
    assert set(matrix) == requirements
    assert set(re.findall(r'^\| (R\d{2}) \|', spec, re.M)) == requirements
    # Check both directions: each case's requirements must match the matrix.
    cases = dict(re.findall(r'^\| (TC-[MS]-\d{3}) \|[^\n]*?\| (R\d{2}[^|]*) \|', document, re.M))
    assert set(cases) == expected
    for requirement, references in matrix.items():
        linked = set(re.findall(r'TC-[MS]-\d{3}', references))
        assert linked and linked <= expected, (requirement, 'unknown case')
        assert linked == {case for case, refs in cases.items()
                          if requirement in re.findall(r'R\d{2}', refs)}, requirement

    def length(node):
        if isinstance(node, (ast.List, ast.Tuple)):
            return len(node.elts)
        if isinstance(node, ast.Name) and node.id == 'BAD_NUMBERS':
            return 5
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return length(node.left) + length(node.right)
        raise AssertionError(ast.dump(node))

    def variants(body):
        # Only loops that introduce subTest represent independent input variants.
        for node in body:
            if isinstance(node, ast.For) and isinstance(node.body[0], ast.With):
                context = node.body[0]
                if any(isinstance(item.context_expr, ast.Call) and
                       isinstance(item.context_expr.func, ast.Attribute) and
                       item.context_expr.func.attr == 'subTest' for item in context.items):
                    return length(node.iter) * variants(context.body)
        return 1

    count = sum(variants(method.body) for method in methods)
    assert count == 137, count
    print(f'OK: {len(requirements)} requirements, {len(methods)} cases, {count} input variants')


if __name__ == '__main__':
    main()
