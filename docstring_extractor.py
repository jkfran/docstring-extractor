import ast
from os.path import basename, splitext

from docstring_parser import parse

NODE_TYPES = {
    ast.ClassDef: "Class",
    ast.FunctionDef: "Function",
    ast.Module: "Module",
}


def parse_docstrings(source):
    """Parse Python source code and yield a tuple of ast node instance, name,
    line number and docstring for each function/method, class and module.

    The line number refers to the first line of the docstring. If there is
    no docstring, it gives the first line of the class, funcion or method
    block, and docstring is None.
    """
    return process_node(ast.parse(source))


def process_node(node):
    """Recursive function to obtain ast nodes"""
    node_type = NODE_TYPES.get(type(node))
    docstring_text = ast.get_docstring(node)
    lineno = getattr(node, "lineno", 0)

    if docstring_text:
        docstring = parse(docstring_text)
    else:
        docstring = None

    # Recursion with supported node types
    children = [
        process_node(n) for n in node.body if isinstance(n, tuple(NODE_TYPES))
    ]

    return {
        "type": node_type,
        "name": getattr(node, "name", None),
        "line": lineno,
        "docstring": docstring,
        "docstring_text": docstring_text if docstring_text else "",
        "content": children,
    }


def get_docstrings(source, module_name=None):
    """Parse Python source code from string and print docstrings.

    For each class, method or function and the module, prints a heading with
    the type, name and line number and then the docstring with normalized
    indentation.

    The module name is determined from the filename, or, if the source is
    passed as a string, from the optional `module` argument.

    The line number refers to the first line of the docstring, if present,
    or the first line of the class, funcion or method block, if there is none.
    """
    if hasattr(source, "read"):
        filename = getattr(source, "name")
        source = source.read()

        if not module_name:
            module_name = splitext(basename(filename))[0]

    docstrings = parse_docstrings(source)

    if module_name:
        docstrings["name"] = module_name

    return docstrings


if __name__ == "__main__":
    import sys

    with open(sys.argv[1]) as file:
        print(get_docstrings(file))
