# Edge Catch Project Brief

## Purpose

Edge Catch is a serious computer science portfolio project intended to
demonstrate the engineering judgment, execution, collaboration, and
technical learning that a strong software internship would normally signal.

The binding delivery and evidence requirements are in `CONTRACT.md`.

## Problem

Software repositories often contain complex or frequently changed functions
that are weakly tested. Coverage tools show what executed, but they do not
necessarily identify:

- which functions deserve testing attention;
- which edge cases matter;
- whether an AI-generated test contains a valid expectation;
- whether a generated test adds meaningful protection;
- whether a failing generated test reveals a bug, ambiguity, environmental
  problem, or incorrect assumption.

## Product idea

Edge Catch should analyze Python repositories that use pytest and help a
developer discover valuable test cases.

The broad envisioned workflow is:

1. Load or clone a repository.
2. Detect or configure how the project and test suite run.
3. Establish a baseline using the existing tests.
4. Analyze source code, coverage, complexity, and relevant Git history.
5. Identify functions that appear risky or weakly tested.
6. Propose structured edge-case hypotheses.
7. Generate candidate tests for selected hypotheses.
8. Execute candidates in an isolated environment.
9. evaluate whether they are valid, stable, nonredundant, and useful.
10. Present the evidence to a human reviewer.

## Candidate signals

Potential analysis signals include:

- statement and branch coverage;
- cyclomatic complexity;
- function size;
- recent change frequency;
- parameter and input complexity;
- exception paths;
- external dependencies;
- existing test patterns.

These signals are suggestions, not predetermined requirements. The planning
process should determine which ones are necessary and defensible.

## Candidate validation methods

Potential validation methods include:

- syntax parsing;
- import success;
- candidate-test execution;
- full-suite regression execution;
- repeat runs for flakiness;
- new line or branch coverage;
- redundancy checks;
- mutation testing;
- human review.

The planning process should determine the smallest credible subset that can
be implemented, evaluated, and shipped by the deadline.

## Important product principle

A failing generated test does not automatically reveal a software bug.

It might instead represent:

- a real behavioral defect;
- specification ambiguity;
- an unsupported generated assumption;
- an environmental or dependency failure;
- a malformed test;
- a redundant or unhelpful test.

The system should preserve the evidence and avoid changing assertions merely
to make generated tests pass.

## Initial boundaries

- Python repositories only.
- pytest only.
- Human review remains part of the workflow.
- The result must be understandable enough that I can defend the code.
- The implementation should minimize unnecessary dependencies, abstractions,
  frameworks, and generated code.
- The product must produce measurable evidence on real repositories.
- Security implications of running repository code must be addressed.

## Learning objective

I want to learn while building this project.

I want to understand and be able to explain:

- Python project structure and packaging;
- AST analysis;
- test discovery and execution;
- coverage and branch coverage;
- complexity metrics;
- subprocesses and isolated execution;
- Docker security boundaries;
- structured AI output;
- test validity and test oracles;
- mutation testing;
- CI, deployment, and PyPI publishing;
- architecture and data-flow decisions;
- evaluation of an AI-assisted engineering system.

Codex should help me reason through these areas rather than hide them behind
large frameworks or produce an entire codebase that I cannot explain.

## Open planning questions

The plan should determine:

- the smallest defensible September product;
- the walking skeleton;
- which features are essential and which should be deferred;
- whether Edge Catch itself should use multiple agents;
- the architecture and data boundaries;
- how generated expectations can be evaluated;
- how untrusted code can be handled safely;
- which open-source repositories make good evaluation targets;
- which metrics make the final claim credible;
- how to obtain maintainer and advisor feedback early;
- what I should implement personally versus delegate to Codex;
- how the AI-assisted development workflow should be documented.