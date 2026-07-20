# Status

This document is an external acceptance contract, not a brainstorming
document. Its requirements may be challenged, but Codex must not silently
weaken, reinterpret, or remove them.

Where a requirement appears risky, create:
1. a risk;
2. a mitigation;
3. an early action;
4. evidence needed to consider it complete.

# Summer Deliverable Contract

**Will Eckenroth & Jason Eckenroth, July 15, 2026**

## Purpose

By September 1, Will will have built and shipped one piece of software that gives a hiring manager the same signals a summer at a strong firm would have given, so that when he applies for 2027 internships this autumn, he competes on equal footing with students who had prestigious work experience.

## The Project

**"The Project" = Edge Catch, unless Will chooses to change it.** Edge Catch is Will's AI multi-agent system that analyzes GitHub repositories, proposes edge cases, generates and implements tests, scores functions, and suggests improvements. Every reference to "the Project" below means Edge Catch or whatever Will designates in its place.

**Decision rule:** the Project stays Edge Catch unless **two or more** confirmed advisors, answering the neutral question, *"What are you looking for from entry-level engineers? What do they need to bring to be an attractive hire?"*, independently indicate this artifact class is the wrong one. **This question closes July 22.** After July 22, the choice of Project belongs to Will alone and does not reopen unless Will reopens it.

## Advisors

Will recruits his own advisors, working engineers and founders who **explicitly agree to the role**. Jason has proposed four candidates (Zack, Andy, Branko, Pawel) and will make soft 1:1 intros. **None is an advisor until they say yes to Will directly.**

- **Lock-down: at least 3 confirmed advisors by the end of Durham (July 22).**
- Will may swap advisors in and out as he pleases. Once locked, the bench stays at 3 or more.
- **Will's ask (his words, roughly this shape):** *"Would you be willing to advise me on my summer project? The goal is to build something that gives a hiring manager the same signals a summer at a strong firm would have given, so when I apply for 2027 internships this autumn, I compete on equal footing with students who had prestigious work experience. Concretely: one short call now, and one or two code reviews in August."*
- **The role (bounded, easy to say yes to):** the entry-level hiring question now; one or two code/design reviews in August (criterion 5); optionally, the end-of-summer demo (criterion 6).
- The relationship is Will's to run: scheduling, agendas, follow-ups, thank-yous.

## Definition of done: six acceptance criteria

A hiring manager comparing Will to an intern from a strong firm is buying six signals. All six must be true by September 1. *What* is built is Will's; *whether it clears this bar* is the contract.

**1. Real problem, real users.**
The Project runs against at least **3 established open-source repositories**, and at least **1 generated-test pull request is merged or substantively reviewed** by a real maintainer. (A merged PR into a real project is the highest-value single line on a 2026 student CV.)

**2. Public, alive, and deployed. Not localhost.**
Public GitHub repo. Installable by a stranger in under 5 minutes (`pip install` from PyPI*) with CI* running on every commit, **plus** a hosted demo (paste a repo URL, get a report). Commit history shows weeks of real iteration, no single-dump upload.

**3. Engineering hygiene.**
The Project has its own tests and CI (a test-generation tool that is itself untested fails on arrival). Evidence of operating it: what broke, what got fixed.

**4. The methodology write-up.**
One to three pages on the AI harness*: how the agents were directed, **how their output was verified**, what failed, what changed. This is the artifact interviews are now built around. Starting from an established harness (e.g., GStack*) and documenting what was adapted and why counts as methodology; adopting one blindly does not.

**5. External review with a no-slop gate.**
At least **2 rounds** of code/design review by working engineers from the advisor bench, with visible changes in response. The final review explicitly certifies **no slop***.

**6. One number and one demo.**
A quantified result (e.g., "found N real bugs / raised coverage X% across M repos") and a demo video of 3 minutes or less, plus a live end-of-summer demo to at least one advisor. Will can defend any line of the code.

## Ownership

- **Will owns:** the idea, the design, the tools, the schedule, the order of work, and how it fits around Durham, California, Mallorca, and Costa Brava.
- **Jason owns:** this bar. It is amendable **only at checkpoints, only with evidence** (e.g., consistent advisor input), not between them.
- The idea does not matter to the hiring manager. **That is exactly why it gets to be Will's.**

## Checkpoints

| Date | What exists |
|---|---|
| **July 22** (end of Durham) | Repo exists; a walking skeleton* runs end-to-end on one real repo, however ugly; **3 or more advisors confirmed**; advisor answers in; Project decision closed; Zack call #1 done or scheduled |
| **Aug 5** (before Mallorca) | Core loop works on 3 repos; first external review requested |
| **Aug 18** (mid Costa Brava) | Deployed: on PyPI with hosted demo live; first PRs submitted to real repos; first review received and changes made; second review requested |
| **Aug 31** (Costa Brava) | All six criteria met; demo delivered |
| **First week of Sept** | CV updated; applications open |

Missing a checkpoint triggers a conversation about scope, not about effort or character.

## Working agreements

- **Start before certain.** The skeleton starts in Durham regardless of pending advisor answers. Every plausible answer still requires a working skeleton.
- **AI is a tool, not a judge.** No model's enthusiasm counts as validation. Validation comes from tests passing, maintainers merging, engineers reviewing, and the numbers in criterion 6.
- **Shipped at 90% beats perfect at 0%.** Publishing something imperfect and iterating in public is not a risk to manage. It is the skill being demonstrated.
- Everything else on the summer list (driving, German, volleyball, constellations, Larkin, the boat) is a good summer, not a competing deliverable. This contract is the one commitment; the rest is life.
- A companion learning track, `will-summer-syllabus.md` in this folder, maps skills, tool decisions, and community engagement to each checkpoint. It is guidance Will adapts, not additional obligation.

## Signatures

**Will Eckenroth** ______________________  Date: ________

**Jason Eckenroth** ____________________  Date: ________

---

## Definitions

*Terms marked with an asterisk above.*

- **CI (continuous integration):** an automated pipeline (e.g., GitHub Actions) that runs the tests, linter, and build on every commit and visibly fails when something breaks. The baseline discipline of every professional engineering team, and the public badge that a repo is operated, not just posted.
- **PyPI (Python Package Index):** the public registry that `pip install` pulls from. Publishing there turns the Project from code that runs on its author's machine into a real, installable product with versioned releases.
- **Harness:** the working setup around an AI coding agent, meaning the instructions, roles, checks, and workflow used to direct the model and verify its output.
- **GStack:** Garry Tan's open-source Claude Code setup (github.com/garrytan/gstack), a packaged harness of roughly 23 skills acting as a virtual engineering team.
- **Slop:** code that produces the output you expect but underneath is a mess: hard-coded fragility, redundant functions doing the same thing, later methods overwriting the work of earlier ones.
- **Walking skeleton:** the smallest possible end-to-end version of the system that actually runs, however ugly, so every later improvement happens on something that already works.
