# ADR-004: Who is an administrator (role set by a server command)

Status: decided by the team after Call 3.

## The question
Kenji asked: who is an administrator, and how does an account become one? A flag, a role, a separate login? Marcus said "we'll figure out the mechanism."

## Options
1. **A role on the accounts table, set only by a command run on the server.**
2. Separate administrator accounts and a separate login page.
3. A role on the accounts table that existing administrators can grant from the admin screen.

## Decision
Option 1. One login for everyone. Each account has a role: buyer or administrator. Registration always creates a buyer. Nobody can become an administrator through the website; an operator runs a command on the server to promote an account.

## Why
- The rule from Call 3 is that a buyer must never be able to do what an administrator does. With option 1 there is no website path to the administrator role at all, so there is nothing to attack through the website.
- One login keeps authentication simple (option 2 means a second path to build and secure).
- Option 3 needs a first administrator anyway and adds a screen that could be abused.

## How it is enforced
- The role is read from the database on every request to an administrator page (not from the browser).
- Signed-out visitor asking for an admin page: redirected to login (same treatment as checkout, decided in Call 3).
- Signed-in buyer asking for an admin page or action: refused, nothing is performed (we use a "forbidden" response).
- Nothing in the buyer-facing flow calls into the Administration component.

## Consequences
- Giving or removing administrator access needs someone with server access. Fine for version one with very few administrators.
- The two redirect/forbidden behaviors for admin pages are our extension of the Call 3 checkout rule. Call 3 only decided the checkout and order-history case.
