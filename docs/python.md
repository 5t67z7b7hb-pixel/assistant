# Python Documentation

**Domain:** Python programming  
**Purpose:** A practical reference for writing, testing, and maintaining
Python applications.

## What Python is

Python is a general-purpose, high-level programming language. It emphasizes
readable syntax and includes a broad standard library. Python programs are
commonly used for automation, web services, data processing, scientific
computing, testing, and AI applications.

Python source is normally executed by an interpreter. A Python implementation
compiles source to bytecode and executes it in a runtime; implementation
details vary. Python is dynamically typed, but type annotations can document
interfaces and help static analysis tools catch mistakes.

## Core values and collections

Common built-in values include integers, floating-point numbers, strings,
Booleans, and `None`. Important collection types are:

- `list`: ordered, mutable sequence.
- `tuple`: ordered, immutable sequence.
- `dict`: mutable mapping of keys to values.
- `set`: collection of distinct hashable values.

```python
person = {"name": "Asha", "skills": ["Python", "SQL"]}
person["active"] = True

for skill in person["skills"]:
    print(skill)
```

Use a dictionary when values are looked up by key, a list when order and
repeated values matter, and a set when membership or uniqueness is central.
Choose immutable values when data should not be changed after creation.

## Functions and modules

Functions package reusable behavior. Give parameters and return values clear
meaning, keep functions focused, and avoid hidden side effects where possible.

```python
def calculate_total(prices: list[float], tax_rate: float = 0.0) -> float:
    """Return the sum of prices with a proportional tax applied."""
    if tax_rate < 0:
        raise ValueError("tax_rate must not be negative")
    return sum(prices) * (1 + tax_rate)
```

Type annotations are not enforced by the Python runtime by default. They
support readers, IDEs, and type checkers. Use modules to organize related
definitions and packages to organize modules. Avoid running substantial
application work merely because a module was imported; use an entry point:

```python
def main() -> None:
    print("Application started")


if __name__ == "__main__":
    main()
```

## Control flow and exceptions

Use `if`/`elif`/`else` for branches, `for` for iterating over an iterable,
and `while` for repetition governed by a condition. Prefer direct iteration
over manual index management when indexes are not needed.

Exceptions communicate error conditions. Catch only errors the current layer
can handle meaningfully, and preserve useful context:

```python
try:
    quantity = int(raw_quantity)
except ValueError as exc:
    raise ValueError("quantity must be a whole number") from exc
```

Do not silently ignore exceptions or return success-shaped fallback values
when an operation failed. Use `finally` for cleanup that must happen regardless
of success, or context managers such as `with open(...)` to manage resources.

## Classes and data modeling

Classes combine state and behavior when an object model makes the domain
clearer. Prefer simple functions and data structures when a class would add
ceremony without improving clarity. Composition is often easier to change
than deep inheritance.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    sku: str
    price: float
```

Dataclasses can generate common methods for data-focused classes. Validate
important invariants explicitly; a type annotation alone does not validate
runtime input.

## Files, paths, and external data

Use `pathlib.Path` for filesystem paths and context managers for files:

```python
from pathlib import Path

text = Path("notes.txt").read_text(encoding="utf-8")
```

Specify text encodings where appropriate. Treat files, environment variables,
network responses, and user input as untrusted. Validate data at boundaries,
handle missing files and permission errors explicitly, and avoid constructing
paths or commands from unvalidated input.

For structured data, use a parser such as Python's `json` module rather than
evaluating text as code. Do not use `eval` or `exec` on data from a user or an
external system.

## Environments and dependencies

Use a virtual environment to isolate project dependencies. Record direct
dependencies and their supported versions in the project's chosen dependency
manifest. Install only packages that are needed, review their provenance, and
keep dependency updates controlled and reproducible. A virtual environment
isolates Python packages; it is not a security sandbox.

## Testing and quality

Tests should verify observable behavior, including normal cases, boundary
conditions, and expected failures. Unit tests cover small components;
integration tests cover boundaries between components; end-to-end tests cover
important user workflows. Make tests deterministic and avoid dependence on
live external services unless the test is specifically designed for that.

Useful quality practices include:

- Follow the style and tooling already established by the project.
- Use a formatter and linter consistently.
- Add type annotations to public interfaces when they clarify the contract.
- Log actionable operational information without exposing secrets or
  unnecessary personal data.
- Review error handling, resource cleanup, and dependency updates.

## Common pitfalls

- Mutable default arguments are created once, not once per call. Prefer
  `None` and create a fresh collection inside the function.
- `is` checks object identity; use `==` for value equality.
- A shallow copy does not recursively copy nested mutable values.
- Catching `Exception` broadly can hide programming errors.
- Floating-point arithmetic can have rounding error; use `decimal.Decimal`
  for calculations that require decimal rounding rules.
- Type hints and input validation solve different problems; external input
  still needs runtime validation.

## Further reading

- Python tutorial: https://docs.python.org/3/tutorial/
- Python library reference: https://docs.python.org/3/library/
- Python language reference: https://docs.python.org/3/reference/
- Python typing documentation: https://docs.python.org/3/library/typing.html
