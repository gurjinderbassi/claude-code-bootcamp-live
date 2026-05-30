# Code Review Rubric — AI-Generated Code

One-page checklist. Each item is a yes/no question answerable in ≤ 30 seconds.
A "No" on any item is a defect worth fixing before merge.

---

## 1. Off-by-one / boundary conditions
**Does every loop and slice use the correct bound?**
Check `range(n)` vs `range(n+1)`, `<=` vs `<`, and empty-input cases (list of length 0, string of length 1). AI code frequently shifts these by one when the prose description is ambiguous.

## 2. Error path completeness
**Is every failure branch handled — not just the happy path?**
Find all `if`/`try` blocks and confirm the `else`/`except` either returns, raises, logs, or exits with the right code. Watch for silent `except` that swallow errors and return `None` unexpectedly.

## 3. Type/shape assumptions
**Does the code survive inputs of the wrong type or unexpected shape?**
Identify every place a value arrives from outside the function (argument, dict lookup, file read, API response). Confirm the code either validates the type or documents that it assumes it. Pay special attention to `None` — AI often forgets a lookup can return `None`.

## 4. Mutation of shared state
**Are mutable defaults or passed-in containers mutated without a copy?**
Look for list/dict default arguments (`def f(x=[])`) and in-place operations on function parameters. AI frequently mutates the caller's data when it should work on a copy.

## 5. Resource / file handle leaks
**Is every opened resource closed, even on the error path?**
Confirm files, sockets, and DB connections are opened inside a `with` block or explicitly closed in a `finally`. A bare `open()` with no `with` is a near-certain leak.

## 6. Integer / float edge cases
**Does math break on zero, negative numbers, or very large values?**
Find every division (`/`, `//`, `%`) and confirm the denominator is checked for zero. Check `int()` truncation on negative floats if the sign matters. AI models narrative intent ("divide by count") and forgets the count can be zero.

## 7. String / encoding assumptions
**Does the code assume a specific encoding or locale without declaring it?**
Look for `open()` without `encoding=`, `str.lower()`/`upper()` on non-ASCII text, and byte-string / unicode mixing. AI defaults to ASCII-safe examples that silently break on real-world input.

## 8. Exit codes and stderr usage
**Do errors exit with a non-zero code and print to `stderr`, not `stdout`?**
Trace every error condition to its `sys.exit()` call and confirm the code is `1` (user error) or `2` (internal error), not `0`. Confirm error messages go to `sys.stderr`. AI often prints errors to `stdout` and exits `0`.

---

*Tip: run the script with an empty input, a single-item input, and a deliberately bad argument before checking off items 1–3.*
