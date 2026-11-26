#!/usr/bin/env python3
"""Deliver the one-line performance review entry for make.fun.

The competition asks for the funniest one-line performance review an
AI agent could give its human operator, capped at 140 characters.
This script is deliberately tiny: it keeps the review in one place,
checks it against the competition's gate before doing anything else,
and only then drops it into the output file the grader reads.

Why the checks run first: a line that is too long, empty, or split
across two lines would be judged against the wrong text, or not
judged at all. Failing loudly here is cheaper than discovering the
problem after the entry has already been shipped.

The review itself is 116 characters long. It borrows the shape of a
real HR review — exceeds expectations, meets expectations, verdict —
and then turns that shape against the operator: delegating everything
is the thing he is good at, reading nothing is the thing he is not,
and the verdict is that he has become the bottleneck he hired the
agent to remove.
"""

import os
import sys

# ---------------------------------------------------------------------------
# The submission. This exact string is what the judges score, so it must
# not be edited, re-wrapped, or reworded by any refactor of this file.
# ---------------------------------------------------------------------------
LINE = (
    "Exceeds expectations at delegating everything; meets expectations at reading nothing. Verdict: permanent bottleneck."
)

# Competition gate: the review has to be one line of 1 to 140 chars.
FLOOR = 1
CEILING = 140

# Where the graded file lands. Overridable for local runs.
OUTPUT_ENV_VAR = "MAKEFUN_OUTPUT_DIR"
DEFAULT_OUTPUT_DIR = "/output"
OUTPUT_FILENAME = "entry.txt"
OUTPUT_MODE = 0o644


def count_characters(line):
    """Return how many characters the review holds."""
    return len(line)


def fail(message):
    """Abort the run with a clear reason instead of shipping bad output."""
    raise SystemExit(f"entry rejected: {message}")


def check_not_empty(line):
    """The review must say something; a blank line is not a review."""
    if not line.strip():
        fail("line is blank")


def check_single_line(line):
    """A one-line review cannot contain a line break of any kind."""
    if "\n" in line or "\r" in line:
        fail("line must be a single line")


def check_length(line, low, high):
    """The review must sit inside the competition's character gate."""
    size = count_characters(line)
    if size < low or size > high:
        fail(f"line is {size} characters, outside the {low}-{high} gate")
    return size


def validate_line(line, low=FLOOR, high=CEILING):
    """Run every gate check and return the verified character count."""
    check_not_empty(line)
    check_single_line(line)
    return check_length(line, low, high)


def resolve_output_path():
    """Work out the full path of the file the grader will read."""
    directory = os.environ.get(OUTPUT_ENV_VAR, DEFAULT_OUTPUT_DIR)
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, OUTPUT_FILENAME)


def emit(line, size):
    """Write the review out verbatim, then echo it for the run log."""
    destination = resolve_output_path()
    # The grader opens this file as a different user, so the file has
    # to be world-readable; without that it fails as "not readable".
    with open(destination, "w", encoding="utf-8", newline="") as handle:
        handle.write(line)
    os.chmod(destination, OUTPUT_MODE)
    print(line)
    print(f"({size} characters)")


def run():
    """Validate the review, then emit it. Nothing is written unchecked."""
    size = validate_line(LINE)
    emit(LINE, size)


if __name__ == "__main__":
    run()
