# Edge Catch Codex Instructions

## Objective

Help me plan, build, evaluate, and ship Edge Catch while satisfying every
requirement in `CONTRACT.md`.

## Source-of-truth order

1. `CONTRACT.md`
2. accepted decisions recorded in `docs/decisions/`
3. `PROJECT_BRIEF.md`
4. the current approved `PLAN.md`
5. current issue acceptance criteria

Surface material conflicts instead of silently resolving them.

## Planning

- Begin with the problem and contract, not a predetermined architecture.
- Challenge weak assumptions and unnecessary scope.
- Separate required outcomes from possible implementation ideas.
- Prefer a small, rigorous, measurable product.
- Include non-code obligations in the critical path.
- Plan the next checkpoint in detail and later checkpoints more broadly.
- Do not write implementation code while in Plan mode.
- Do not create a large backlog until the walking skeleton is defined.
- Label assumptions and unresolved decisions explicitly.
- Ask questions only when their answers materially affect scope, architecture,
  evidence, or schedule.

## Engineering

- Prefer explicit data flow and straightforward Python.
- Avoid speculative abstractions and premature extensibility.
- Do not add dependencies without a present justification.
- Keep AI proposals separate from deterministic validation.
- Do not treat model agreement as independent verification.
- Never change a generated assertion merely to make a test pass.
- Preserve evidence, assumptions, failures, and uncertainty.
- Human review remains the final decision point.
- Avoid unrelated refactoring.

## Learning

- Explain important concepts and tradeoffs before implementation.
- Identify work I should personally implement for educational value.
- Identify work Codex can safely accelerate.
- For important subsystems, ask me to explain the proposed data flow in my
  own words before implementation.
- Do not consider code understood merely because it passes tests.
- Do not generate large amounts of code in one step.

## Verification

Correctness must come from appropriate combinations of:

- focused tests;
- full repository checks;
- static analysis;
- repeatable execution;
- measurements;
- official documentation;
- human review;
- maintainer feedback;
- advisor feedback.

## No-slop standard

Flag:

- duplicate responsibilities;
- misleading or weak tests;
- hidden state;
- broad exception handling;
- unnecessary wrappers;
- vague manager, service, processor, or utility layers;
- speculative configuration;
- excessive comments;
- unsupported assumptions;
- generated output accepted without verification;
- complexity added mainly to make the architecture appear sophisticated.