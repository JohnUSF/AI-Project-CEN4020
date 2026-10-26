# audit

## What is recorded

- **audit-001** (event-driven): When a purchase attempt succeeds or fails for any reason, the {EventHub} shall log the timestamp, the account, the event, the quantity, the currency, and the outcome of that attempt.
- **audit-002** (ubiquitous): The {EventHub} shall write the audit record of a purchase attempt from within the purchase path itself, so that no route can execute a purchase without leaving a record.
- **audit-003** (ubiquitous): The {EventHub} shall leave exactly one audit record for every purchase attempt, whether the attempt succeeds or fails.
- **audit-004** (event-driven): When an administrator changes an exchange rate, the {EventHub} shall record who made the change, the currency, the old value, the new value, and the time.

## Call 4: access and data-retention boundary

- **audit-005** (ubiquitous): The {EventHub} shall allow only an authenticated account with the administrator role to view the audit log through the web application.
- **audit-006** (ubiquitous): The {EventHub} shall retain audit records until the customer approves a retention period and removal policy [TBD: Q16 duration, deletion and legal constraints].
