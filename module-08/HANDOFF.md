# Handoff: pricing.py Readability Refactor

## What Changed
- Replaced deeply nested `if/else` conditionals in the item loop with early `continue` guards, flattening the logic from ~7 levels to 2.
- Extracted `TAX_RATES` and `COUPON_FACTORS` into module-level dicts, replacing the `if/elif` chains for tax and coupon lookup.
- Flattened the shipping tiers from nested `if/else` into a sequential early-return guard pattern (highest threshold first).

## Why
The original code was unreadable due to cascading nesting and `pass`-padded branches. No logic was changed — this is a readability-only pass per the constraints in `constraints.md`.

## Risk + How to Roll Back
**Risk:** Low. Public API (`calc` signature), module-level imports, and all test outputs are byte-identical.
**Roll back:** `git revert` the refactor commit. No migration, no config change needed.

## Watch-outs for the Next Engineer
- `COUPON_FACTORS` is the single source of truth for discount codes — add new coupons there, not inline.
- `TAX_RATES.get(country, 0.10)` silently applies 10% to any unknown country code; validate `country` upstream if stricter behavior is needed.
- VIP discount and coupon discount are mutually exclusive: VIP wins. This mirrors the original logic — don't change it without a test update.
- The item loop skips `None`, wrong-length tuples, and non-positive qty/price silently. If you need error reporting on bad input, add it at the call site.
