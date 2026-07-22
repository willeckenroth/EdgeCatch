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
- Will completed the AST/proposal teach-back on July 21. Focused tests and public
  Python 3.11/3.12 CI passed before the next slice began.

## 2026-07-21: exact temporary repository preparation

- Will completed the AST/proposal teach-back before repository preparation
  began.
- Codex drafted a context-managed repository boundary that accepts an existing
  local directory or HTTPS GitHub URL plus a full commit identifier.
- Preparation creates an independent clone, checks out the requested commit,
  verifies the resolved commit, preserves each Git command result, and removes
  the workspace when its context ends.
- Will completed the repository-preparation teach-back on July 22. Focused tests
  and public Python 3.11/3.12 CI passed before reporting work began.

## 2026-07-22: versioned evidence reports

- Will completed the exact-commit temporary-repository teach-back before report
  implementation began.
- Codex drafted small evidence dataclasses for repository preparation, baseline,
  coverage summary, proposal provenance, validation, and the final analysis.
- `report.json` is the versioned source of truth. `report.md` is rendered from
  the same in-memory report rather than assembled through a second data path.
- Missing stages remain explicit null values, while commands preserve arguments,
  working directory, output, errors, exit status, duration, and timeout state.
- Will completed the report teach-back on July 22. Focused tests and public
  Python 3.11/3.12 CI passed before pipeline composition began.

## 2026-07-22: deterministic recorded-proposal pipeline

- Will completed the report data-flow teach-back before pipeline composition.
- The first vertical pipeline intentionally uses the current Python environment
  and a recorded proposal. Dedicated target environments, coverage, and live
  model calls remain explicit missing stages rather than implied features.
- Candidate code is parsed before writing, collected and run separately, then
  followed by the full suite and one repeat only while prior checks succeed.
- The candidate is written only inside the temporary clone. The integration
  fixture verifies the original repository never receives the candidate file.
- Malformed model JSON and invalid candidate syntax are preserved and classified
  as invalid generation rather than repaired or discarded.
- The first CLI smoke command omitted virtual-environment activation, so the
  shell could not locate `edge-catch`. Invoking `.venv/bin/edge-catch` directly
  succeeded and displayed both top-level and `analyze` help.
- The README explicitly warns that a recorded proposal becomes executable code;
  a temporary clone protects the original checkout but is not an operating-
  system sandbox.
- Review found that the first pipeline draft combined orchestration and
  candidate execution. Candidate parsing and execution moved to `validation.py`
  so `pipeline.py` remains responsible for stage order and evidence assembly.
- Automatic classification is limited to objective invalid-generation and
  launch/timeout outcomes. Passing or behaviorally failing candidates remain
  unreviewed until Will defines and applies the oracle policy.
- Focused verification and human review of this slice are pending.

## 2026-07-22: target environment and branch coverage

- The humanize preflight pinned commit
  `c3a124cdeb272d7f63bc0aa66f79c6fbafd2fc6d` and found that its test extra now
  requires pytest 9, while Edge Catch development currently uses pytest 8. This
  confirmed the need for a separate target environment.
- Coverage.py is the first runtime dependency. Edge Catch wraps the configured
  `python -m pytest` arguments in branch coverage, exports versioned JSON, and
  strictly parses totals plus missing lines and branches for the prompt.
- The first environment attempt used `venv --system-site-packages`, but a venv
  created from another venv sees the base interpreter's global packages rather
  than the parent venv. The baseline failed with `No module named coverage`.
- That assumption was removed. A real target environment now installs the exact
  Edge Catch coverage.py version through a separately recorded pip command.
- Network-free integration tests use an explicitly supplied existing test
  environment. The pinned humanize run is responsible for exercising the real
  environment-creation and tooling-install path.
- The test command must begin with `python -m pytest`, making the coverage
  wrapping rule explicit instead of pretending arbitrary commands are supported.
- All 40 local tests and public Python 3.11/3.12 CI checks passed.
- The first pinned humanize pass exercised the real environment path: both
  environment commands, editable test-extra installation, baseline suite, and
  coverage export passed. It measured 541/549 lines and 207/216 branches, with
  line 175 and branch `174 -> 175` missing inside `intcomma`.
- A deliberate invalid placeholder produced and preserved the coverage-informed
  prompt without executing generated code.
- The first inference request used GitHub's documented endpoint, API version,
  `openai/gpt-4.1`, temperature 0, and JSON-object response mode. GitHub rejected
  it with HTTP 401 because the stored CLI token lacks Models inference access;
  no model output was generated. The available browser session was also signed
  out, so work paused for explicit user authentication rather than requesting or
  exposing a credential. See the [official inference documentation](https://docs.github.com/en/rest/models/inference).
