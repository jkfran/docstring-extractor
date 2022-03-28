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
        try:
            docstring = parse(docstring_text)
        except Exception:
            docstring = None
    else:
        docstring = None

    params = {
        "attributes": [],
        "arguments": [],
        "returns": None,
    }

    description = {
        "short": None,
        "long": None,
    }

    arguments = []
    if node_type == "Function":
        args = getattr(getattr(node, "args"), "args")

        for arg in args:
            name = getattr(arg, "arg")
            annotation = getattr(arg, "annotation")
            arguments.append(
                {
                    "name": name,
                    "type": getattr(annotation, "id", None)
                    if annotation
                    else None,
                }
            )

    if docstring:
        # Extract parameters
        if docstring.params:
            for param in docstring.params:
                if param.args[0] == "attribute":
                    params["attributes"].append(
                        {
                            "name": param.arg_name,
                            "type_name": param.type_name,
                            "is_optional": param.is_optional,
                            "description": param.description,
                            "default": param.default,
                        }
                    )
                elif param.args[0] == "param":
                    params["arguments"].append(
                        {
                            "name": param.arg_name,
                            "type_name": param.type_name,
                            "is_optional": param.is_optional,
                            "description": param.description,
                            "default": param.default,
                        }
                    )
        if docstring.returns:
            params["returns"] = {
                "name": docstring.returns.return_name,
                "type_name": docstring.returns.type_name,
                "is_generator": docstring.returns.is_generator,
                "description": docstring.returns.description,
            }
        # Extract description
        if docstring.blank_after_short_description:
            if docstring.long_description:
                description["short"] = docstring.short_description
                description["long"] = docstring.long_description
            else:
                description["short"] = docstring.short_description
        elif docstring.short_description:
            description[
                "long"
            ] = f"{docstring.short_description} {docstring.long_description}"
        else:
            description["long"] = docstring.long_description

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
        "params": params,
        "description": description,
        "arguments": arguments,
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
