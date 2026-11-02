# ADR-007: Per-account limit on purchase request speed

Status: implemented with **provisional numbers**; the numbers are open item Q19.

## The question
Kenji: the purchase limit "handles per-account quantity, but nothing constrains how fast requests arrive. A script hammering the purchase endpoint two hundred times a minute looks, to the current build, like an enthusiastic student." Priya: "Something for the backlog." Kenji: his findings block release.

## Options
1. **Sliding window per signed-in account, in application memory.** Over the limit: HTTP 429 with a wait time, nothing created.
2. Per-IP limit. A campus network puts thousands of students behind a few addresses, so this would block real buyers.
3. Put it in the database so several workers share it. Correct for many processes, but adds a write to every purchase request on the path that already serializes all writers (ADR-001).
4. Leave it for the backlog and formally accept the risk.

## Decision
Option 1. Purchase requires sign-in, so the account is the right key (option 2 is wrong for a campus).

## Provisional numbers
20 purchase requests per account per 60 seconds, settable with `EVENTHUB_PURCHASE_RATE_LIMIT` and `EVENTHUB_PURCHASE_RATE_WINDOW` (0 turns it off). **The customer has not given a number.** A person using the site cannot reach 20 purchases a minute; a script reaches 200 easily. The team chose 20 so the control can be tested, not because anyone approved it.

## Behaviour
- Rejected requests are not counted, so hammering does not extend the block.
- Every rejected request is answered with a message and a `Retry-After` header.
- Only the **first** rejection of a blocked period writes an audit entry (`audit-007`). One row per rejected request would let an attacker flood the audit table, which is a different attack on the same system.
- Failed validations count too: the abuse is the request rate, not the outcome.

## Limits we are stating plainly
- State is per process and resets on restart. Several worker processes would each allow the full number. Fine for the one-process classroom build; a real deployment needs a shared store.
- It slows a single account. It does nothing about one person registering many accounts. That needs the email verification decision (Q3).
- It protects the purchase endpoints only. Login attempts are not limited.
