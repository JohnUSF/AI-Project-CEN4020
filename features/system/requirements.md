# system

## Platform and boundary

- **system-001** (ubiquitous): The {EventHub} shall be implemented in Python using Flask for version one.
- **system-002** (ubiquitous): The {EventHub} shall validate every piece of data that crosses into the system boundary before any internal component trusts or uses it.
- **system-003** (ubiquitous): The {EventHub} shall render its web pages in a layout that adapts to mobile phone screen sizes.

## Sessions

- **system-004** (state-driven): While a session has been idle for [TBD: Q11 expiry duration], the {EventHub} shall expire the session and require the account to sign in again.
- **system-005** (ubiquitous): The {EventHub} shall read the session idle timeout from application settings, so that changing it needs no code change.

## Performance

- **system-006** (state-driven): While [TBD: Q13 peak number of simultaneous buyers] buyers are active, the {EventHub} shall respond to a purchase request within [TBD: Q13 response-time target].

## Call 4: testability and implementation agreement

- **system-007** (ubiquitous): The {EventHub} shall keep identity, catalog, discount eligibility, pricing, inventory, purchase, audit and administration logic independently importable and testable.
- **system-008** (ubiquitous): The {EventHub} shall run automated tests on the shared source branch before an implementation change is considered complete.

## Call 5: tests that trace to the specification

- **system-009** (ubiquitous): The {EventHub} shall carry a requirement identifier on every automated test, so that a failing test names the requirement it protects.

## Call 6: maintenance and internationalization

- **system-010** (event-driven): When a reader selects Spanish, the {EventHub} shall show its core navigation, registration, event discovery, checkout and order-history interface in Spanish and allow switching back to English.
- **system-011** (event-driven): When the reader selects a supported language, the {EventHub} shall display event dates using that language's regional date convention without changing the saved event timestamp [ASSUMPTION: Q24 locale and time-zone policy pending].
- **system-012** (event-driven): When a maintenance operator backs up the SQLite database, the {EventHub} shall create and verify a consistent backup including committed transactions and store a checksum alongside it [TBD: Q25 owner, schedule and offsite retention].
- **system-013** (event-driven): When an operator restores a backup, the {EventHub} shall require explicit offline confirmation, check the saved checksum and database integrity, and reject tampered copies.
