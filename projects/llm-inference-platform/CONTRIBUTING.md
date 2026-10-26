# Feedback and contributions

Kumar Raja Annamreddi is the maintainer of this independent project. Bug reports,
questions, reproducibility reports, and suggestions are welcome.

## Current contribution policy

**External code and documentation patches are not being accepted at this stage.**
Please open an issue describing a problem or proposed behavior instead of
submitting a pull request. Do not paste substantial implementation code,
confidential information, prompts containing private data, or access tokens.

This keeps authorship and licensing boundaries straightforward while the project
is developed. Opening an issue, signing a commit, or submitting a patch does not
automatically transfer your copyright to the maintainer. If external patches are
accepted later, contribution terms and any necessary written rights agreement
will be established before incorporating them. Unsolicited patches will not be
merged under an assumption of ownership transfer.

You may fork, modify, and redistribute the project under the [Apache License
2.0](LICENSE), including commercially. This contribution policy governs what is
accepted into this repository; it does not restrict those license permissions.
Preserve applicable notices, identify modified files, and do not imply endorsement
by the maintainer.

## Useful bug reports

Include the Python version, operating system, backend type, minimal steps,
expected behavior, actual behavior, and relevant sanitized logs. Synthetic
reproductions are preferred because they run without model downloads or charges.
Do not upload `.env` files, real tokens, private model inputs, or employer data.

For a security concern that could expose credentials or data, contact
kr.annamreddi@gmail.com privately before posting details publicly. No paid bug
bounty or response-time commitment is offered.

## Local verification

Follow the README setup and run:

```bash
python -m pytest -q
python tools/benchmark.py
```

A passing synthetic benchmark does not verify real-model or GPU performance.
