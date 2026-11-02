# ADR-008: The student discount is judged from the current email at every price

Status: decided by the team after Call 5. The email-change policy itself is open item Q18.

## The question
Kenji: "I registered with a USF address, got the discount. Then I changed my account email to a non-USF address. My discount stayed. Eligibility was checked at registration and never again."

## What the Part 4 build actually does
We tried to reproduce this and could not. In this build:
- there is no screen, route or function that changes an account's email address (only `UPDATE accounts SET role` and `currency` exist), and
- `purchase.place_order` calls `eligible_for_usf_discount(buyer["email"])` on the account row it reads **inside the purchase transaction**, and the event page and live estimate do the same for every view.

So the discount follows whatever email is in the database at that moment. The finding describes a risk the build does not have today, but it holds only by accident: nothing in the requirements said so, and no test would have caught a later change that cached the answer.

## Decision
1. Write the property down (`pricing-015`) and test it, including a mutation that caches eligibility per account (M09 in `scripts/mutation_check.py`).
2. State that the website offers no email change in version one (`identity-020`), with the policy question left as Q18 for the customer: may buyers change their email at all, and must a new address be verified?
3. Do not invent that policy. The director's own words were "requirements gap; it goes to email."

## What this does not fix (RISK-001)
Nothing proves that someone registering `friend@usf.edu` owns that mailbox (open item Q3, unanswered since Part 1). Anyone can register with a USF address and get the discount. This is the real hole behind Kenji's story. It is recorded in `docs/risk-register.md` for the customer to accept or to fund a fix (for example, a confirmation link sent to the address).

## Consequences
- If a future email-change feature is added, the discount will correctly follow the new address with no extra code. Whether the old address's past orders keep their discount is unaffected: each order stores the discount it was charged.
- The characterization test `test_known_risk_an_unverified_usf_address_is_eligible` documents today's behaviour and is the test to change when Q3 is decided.
