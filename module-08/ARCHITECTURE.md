# Architecture: pricing.py

## Data Flow

```
 caller
   |
   |  items: list[tuple]
   |  country: str
   |  customer: dict | None
   v
+------------------+     COUPON_FACTORS     +-------------------+
|   Item Loop      | --(coupon lookup)----> |  Discount Engine  |
|  (validation +   | <--(factor)-----------| VIP: 10% off      |
|   subtotal acc.) |                        | SAVE10: 10% off   |
+------------------+                        | SAVE20: 20% off   |
   |                                        +-------------------+
   |  subtotal
   v
+------------------+     TAX_RATES
|   Tax Engine     | --(country lookup)---> {US,GB,DE,FR,default}
+------------------+
   |  tax
   v
+------------------+
|  Shipping Engine |  <50 → $9.99 | 50–199 → $4.99 | 200+ → free
+------------------+
   |  ship
   v
 round(subtotal + tax + ship, 2)  →  final price (float)
```

## Components

**Item Loop** — Iterates `items`, skipping `None`, wrong-length tuples, and
non-positive qty or unit_price. For each valid item it computes `qty *
unit_price`, applies the discount engine, and accumulates into `subtotal`.
Input: raw item list + customer dict. Output: `subtotal` (float).

**Discount Engine** — Applies at most one discount per line item. VIP flag
takes priority; if absent, looks up the coupon code in `COUPON_FACTORS`. The
two are mutually exclusive by design. Input: `line` amount + customer dict.
Output: discounted `line` amount.

**TAX_RATES** — Module-level dict mapping ISO-2 country codes to tax rates.
Falls back to 10% for any unknown code. Input: `country` string. Output: tax
rate (float).

**Tax Engine** — Multiplies `subtotal` by the rate from `TAX_RATES`.
Input: `subtotal`, `country`. Output: `tax` (float).

**Shipping Engine** — Three-tier flat-rate logic based on `subtotal` thresholds
($50, $200). Input: `subtotal`. Output: `ship` (float).

## Known Limitations

1. Only four countries have explicit tax rates; all others silently get 10% —
   no warning is raised for unknown country codes.
2. Discount model is closed: adding a new coupon requires editing
   `COUPON_FACTORS`; there is no runtime registration mechanism.
3. VIP and coupon discounts are always mutually exclusive — stacking is
   impossible without a logic change.
4. Shipping tiers are hardcoded; currency, locale, or weight-based shipping
   cannot be expressed.
5. Invalid items (wrong length, negative price) are silently skipped with no
   error surfaced to the caller.
