# docstring-extractor

Get Python docstrings from files or Python source code.

Example usage:

```python
>>> from docstring_extractor import get_docstrings
>>>
>>> with open("example.py") as file:
...     get_docstrings(file)
...

{
    'module': 'example',
    'content': [{
        'type': 'Function',
        'name': 'my_fuction',
        'line': 4,
        'docstring': 'Long description spanning multiple lines\n- First line\n- Second line\n- Third line\n\n:param name: description 1\n:param int priority: description 2\n:param str sender: description 3\n:raises ValueError: if name is invalid'
    }]
}
```

# Contributing

This project uses [Black](https://github.com/psf/black).
