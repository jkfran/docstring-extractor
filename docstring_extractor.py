import ast

from os.path import basename, splitext


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
    docstring = ast.get_docstring(node)
    lineno = getattr(node, "lineno", 0)

    # Recursion with supported node types
    children = [
        process_node(n) for n in node.body if isinstance(n, tuple(NODE_TYPES))
    ]

    return {
        "type": node_type,
        "name": getattr(node, "name", None),
        "line": lineno,
        "docstring": docstring if docstring else "",
        "signature": get_signature(node) if node_type == "Function" else None,
        "content": children,
    }


def get_signature(node):
    args = []

    if node.args.args:
        [args.append([a.col_offset, a.arg]) for a in node.args.args]
    if node.args.defaults:
        for a in node.args.defaults:
            if isinstance(a.value, str):
                value = f"'{a.value}'"
            else:
                value = str(a.value)

            args.append([a.col_offset, "=" + value])

    sorted_args = sorted(args)
    for i, p in enumerate(sorted_args):
        if p[1].startswith("="):
            sorted_args[i - 1][1] += p[1]
    sorted_args = [k[1] for k in sorted_args if not k[1].startswith("=")]

    if node.args.vararg:
        sorted_args.append("*" + node.args.vararg)
    if node.args.kwarg:
        sorted_args.append("**" + node.args.kwarg)

    if sorted_args:
        return "(" + ", ".join(sorted_args) + ")"

    return None


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
