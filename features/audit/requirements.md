# audit

## What is recorded

- **audit-001** (event-driven): When a purchase attempt succeeds or fails for any reason, the {EventHub} shall log the timestamp, the account, the event, the quantity, the currency, and the outcome of that attempt.
- **audit-002** (ubiquitous): The {EventHub} shall write the audit record of a purchase attempt from within the purchase path itself, so that no route can execute a purchase without leaving a record.
- **audit-003** (ubiquitous): The {EventHub} shall leave exactly one audit record for every purchase attempt, whether the attempt succeeds or fails.
- **audit-004** (event-driven): When an administrator changes an exchange rate, the {EventHub} shall record who made the change, the currency, the old value, the new value, and the time.
