# Methodology log

This is a contemporaneous record of how AI assistance is used and verified.
It records failures and uncertainty rather than treating generated output as
correct by default.

## 2026-07-20: package skeleton

- Codex drafted the package structure, CLI, tests, build metadata, and CI in a
  bounded EC-001 slice.
- Will reviewed the purpose of the repository directories and explained the
  seven-stage Edge Catch data flow in his own words before EC-002 began.
- Local verification covered CLI behavior, tests, lint, isolated package
  builds, and installation of the built wheel in a clean virtual environment.
- The first isolated build failed because the execution sandbox could not
  reach PyPI. It passed when explicitly rerun with network access; this was an
  environment restriction, not a package defect.
- The first public CI run passed but warned that two actions used deprecated
  Node.js 20 runtimes. Their current official major versions were verified,
  updated, and the replacement Python 3.11/3.12 CI run passed without those
  warnings.

## 2026-07-20: repository configuration and command runner

- Repository commands are TOML arrays of arguments, not shell command strings.
  This keeps argument boundaries explicit and prevents shell interpretation.
- The runner captures the command, working directory, output, exit code,
  duration, timeout status, and launch error without converting failures into
  success.
- A timed-out process is placed in its own process group and that group is
  killed, reducing the chance of child processes surviving the timeout.
- Focused tests exercise successful execution, nonzero exit, timeout, missing
  executable, valid configuration, and rejected unsafe configuration shapes.
- Will completed the runner teach-back on July 21, correctly distinguishing
  configuration validation, direct argument-array execution, nonzero exits,
  launch errors, timeouts, and higher-level policy decisions.

## 2026-07-21: explicit AST target and recorded proposal boundary

- Codex drafted a bounded slice that extracts one explicitly named function
  with the standard-library AST and validates a recorded JSON proposal.
- AST extraction records exact source boundaries, signature, docstring, and
  qualified name. It does not yet rank functions or interpret coverage.
- Proposal parsing requires the agreed fields and preserves the exact raw
  response. It does not parse, run, repair, or approve the candidate test.
- The first focused test run exposed that `ast.unparse` normalizes signature
  spacing and quote style. The exact source remains separately preserved; the
  signature test was corrected to verify the intentional canonical form.
- A non-isolated package build failed because the development environment does
  not contain its own copy of setuptools. The normal isolated build initially
  hit the execution sandbox's network restriction, then succeeded with approved
  access and included both new modules in the source and wheel distributions.
- Human review, focused verification, and teach-back of this slice are pending.
