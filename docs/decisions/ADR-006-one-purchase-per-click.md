# ADR-006: A repeated "buy" returns the original order (purchase token)

Status: proposed by the team after Call 5. **Needs customer confirmation (open item Q20).**

## The question
Thuy: "If the buy button fires twice (slow page, impatient thumb) do we create two orders? One? Reject the second? Nothing in the requirements says." Priya called an accidental double purchase "the most common real-world checkout bug there is."

## Options
1. **A one-time purchase token in every form.** The server remembers the token on the order it created. A second request with the same token returns the original order. No second order, no second ticket taken.
2. Reject the second request with an error. Safe, but the buyer who double-clicked sees a failure message for a purchase that actually succeeded, which is exactly the "did I get charged?" confusion Darnell's students reported on the confirmation page.
3. Refuse any purchase of the same event by the same account within N seconds. Stops legitimate repeat buys and needs a number nobody has given us.
4. Only disable the button with JavaScript. Does nothing for a slow connection, a second tab, a script or the Back button.

## Decision
Option 1, plus a JavaScript guard (disable the button on first submit) as a convenience. The server rule is the one that counts.

## How it works
- Every checkout form and every quick-buy form gets a new random token each time the page is shown (`purchase-025`).
- Inside the same write lock that protects the ticket count, the purchase checks whether this account already has an order with this token. If so it records `duplicate_suppressed` in the audit log and returns that order (`purchase-024`).
- The same token reused for a different event, quantity or currency is refused (`purchase-026`). A form with no valid token is refused (`purchase-028`).
- The token is stored only on orders. A failed attempt (sold out, say) leaves the token free to retry.
- A database unique index on (account, token) is the backstop if the check were ever bypassed.

## Consequences
- A page left open cannot buy twice. Buying again on purpose means loading the checkout page again, which gets a new token.
- Back-button restores from the browser cache may carry an old token. The result is the original order, never a second one.
- `audit-003` ("exactly one record per attempt") is reworded as `audit-008` so a duplicate counts as an attempt that leaves one record.
- Existing orders from Part 4 have no token and are unaffected (the migration adds the column as empty).
