# Edge Catch

Edge Catch is a human-in-the-loop tool for proposing and validating valuable
edge-case tests in trusted Python repositories that use pytest.

The project is at the walking-skeleton stage. A recorded-proposal pipeline now
prepares an exact commit, runs the baseline suite, extracts an explicit AST
target, validates a candidate test, and writes versioned JSON and Markdown
reports. Target commands run in a dedicated virtual environment, and baseline
and post-candidate branch coverage are recorded. Automatic target ranking and
live AI calls are not implemented yet. The binding delivery requirements are in
[`CONTRACT.md`](CONTRACT.md).

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

Run the deterministic recorded-proposal pipeline:

```console
edge-catch analyze REPOSITORY \
  --commit FULL_COMMIT_SHA \
  --config repository.toml \
  --output reports \
  --target src/package/module.py:function_name \
  --proposal proposal.json \
  --model MODEL_IDENTIFIER
```

The proposal contains Python code that Edge Catch will execute. Inspect and
trust the recorded proposal before running this command. Candidate execution is
isolated from the original checkout by a temporary clone, but it is not a secure
operating-system sandbox.

## Security boundary

The finished CLI will execute repository tests only when the user explicitly
trusts the target repository. The planned hosted demo will never execute code
from an arbitrary pasted repository URL. These boundaries are requirements,
not claims about functionality already implemented.
