# Humanize walking-skeleton evidence

- Repository: `https://github.com/python-humanize/humanize`
- Commit: `c3a124cdeb272d7f63bc0aa66f79c6fbafd2fc6d`
- Manual target: `src/humanize/number.py:intcomma`

## Prompt run

The `prompt-run` directory records a deliberate first pass using
`invalid-proposal.txt`. Its purpose is to exercise repository preparation,
dedicated-environment creation, installation, baseline testing, branch coverage,
AST extraction, and prompt construction without executing generated code.

Observed baseline:

- full pytest suite passed;
- 541/549 lines covered;
- 207/216 branches covered;
- `intcomma` missing line 175 and branch `174 -> 175`.

The `invalid generation` classification is expected because the placeholder is
deliberately not JSON. It is not a model response.

## Model status

The first inference request was rejected with HTTP 401 because the existing
GitHub CLI token lacks GitHub Models inference permission. No model output was
generated. The successful model request and final validation report remain
pending authentication with `models: read` permission.
