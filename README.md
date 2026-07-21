# Edge Catch

Edge Catch is a human-in-the-loop tool for proposing and validating valuable
edge-case tests in trusted Python repositories that use pytest.

The project is at the early walking-skeleton stage. Repository configuration,
command evidence capture, explicit AST target extraction, and recorded proposal
parsing are implemented. Coverage analysis, live AI calls, candidate validation,
and final reporting are not implemented yet. The binding delivery requirements
are in [`CONTRACT.md`](CONTRACT.md).

## Development setup

Edge Catch supports Python 3.11 and 3.12.

```console
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Verify the package:

```console
edge-catch --help
python -m pytest
ruff check .
python -m build
```

## Security boundary

The finished CLI will execute repository tests only when the user explicitly
trusts the target repository. The planned hosted demo will never execute code
from an arbitrary pasted repository URL. These boundaries are requirements,
not claims about functionality already implemented.
