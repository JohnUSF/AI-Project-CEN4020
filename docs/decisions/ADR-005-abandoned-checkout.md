# ADR-005: Abandoned checkouts (clean cancel and audit event, no lock-in)

Status: decided by the team after Call 3.

## The question
Marcus asked to "lock buyers in": disable the Back button and stop them closing the tab until they finish or press cancel, because half-finished checkouts are "data garbage". Priya turned the need into "handle abandoned checkouts cleanly" and left the treatment to the build.

## Options
1. **Clean cancel plus an audit event.** No order exists until the simulated payment succeeds, so an abandoned checkout leaves no half-order. Cancelling, or leaving the page, writes an "abandoned" record to the audit log.
2. Lock-in as asked: warn on leaving and block in-app navigation.
3. A "pending order" row that a background job cancels after a timeout.

## Decision
Option 1.

## Why
- Web pages cannot truly disable the Back button or the tab close button. They can only show the browser's own "Leave site?" prompt. Promising a lock-in would promise something we cannot build.
- Marcus's real goal is clean funnel data. If no order is created before payment succeeds, the orders data cannot be polluted at all, and abandoned attempts are counted from the audit log.
- Option 3 behaves like a ticket hold, which conflicts with the still-open hold or no-hold question (Q5).

## Consequences and limits
- Detecting "left the page" depends on the browser sending a signal when the page closes. This is best effort. A buyer who just loses signal leaves no abandoned record, so funnel numbers are a floor, not an exact count.
- We did not add a "checkout started" record. If Marcus wants an exact funnel (started vs finished vs cancelled), that is a small follow-up requirement.
- The requirement purchase-023 states plainly that EventHub does not block Back or tab close, so the decision is testable and visible.
