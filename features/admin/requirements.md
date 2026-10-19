# admin

## Access to the administrator area

- **admin-001** (ubiquitous): The {EventHub} shall provide an administrator area in which administrators update exchange rates and read the audit log.
- **admin-002** (unwanted): If a visitor who is not signed in requests an administrator page, then the {EventHub} shall redirect the visitor to the login page and show no administrator content.
- **admin-003** (unwanted): If a signed-in account without the administrator role requests an administrator page or action, then the {EventHub} shall refuse the request and perform no part of it.
- **admin-004** (ubiquitous): The {EventHub} shall check the administrator role on the server for every request to an administrator page, whatever the browser shows or hides.
- **admin-005** (ubiquitous): The {EventHub} shall expose the administrator area only to accounts that hold the administrator role and shall let no buyer-facing page or action call into it.

## Exchange rates and audit log

- **admin-006** (complex): While an administrator is signed in, when the administrator submits a new exchange rate for a supported currency, the {EventHub} shall store the rate in the database.
- **admin-007** (unwanted): If a submitted exchange rate is not a positive decimal number or names a currency that is not supported, then the {EventHub} shall reject the change and keep the current rate.
- **admin-008** (event-driven): When an administrator opens the audit log, the {EventHub} shall list the audit records newest first, so that a dispute can be investigated without opening the database files by hand [TBD: Q12 how administrators search or filter records].
