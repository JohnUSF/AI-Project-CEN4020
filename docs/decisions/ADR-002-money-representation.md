# ADR-002: How money is represented (whole minor units)

Status: decided by the team after Call 3.

## The question
Kenji's constraint: computers do surprising things with decimal money, and currencies disagree about decimal places (yen has none). If we do not choose on purpose, the machine chooses silently.

## Options
1. **Integer minor units.** Store 4999 for $49.99 and 5000 for 5000 yen. A small table says how many digits each currency has (USD 2, EUR 2, GBP 2, JPY 0).
2. **Python Decimal.** Exact decimals, rounded to each currency's precision at the end.

## Decision
Every monetary amount is a whole number of the currency's smallest unit, held as an integer in the database and in code. Floating-point numbers are never used for money.

## Details
- The digits-per-currency table lives in the configuration file next to the supported-currency list (Q7 is still open, so the list itself is not final).
- Exchange rates are not money. They are stored as decimal text, checked at the boundary (positive, limited digits), and read with Python's `Decimal` only inside the pricing component to do the conversion. The result is turned back into an integer minor unit.
- Rounding happens once, at the end, inside pricing. **The rounding mode and whether the discount is taken before or after conversion are still open (Q8).** Because all of it lives in one function in pricing, the answer is a one-place change.
- Each order stores its currency, the rate applied, and the total as integers, so an old order never changes when rates change later.

## Consequences
- Adding up, comparing and storing amounts is exact. No "0.1 + 0.2" surprises.
- Every place that shows a price must format minor units using the currency's digits (yen shows no decimals).
- Mixing two currencies without converting is a bug the type of the value should make obvious (we keep the currency code next to every amount).
