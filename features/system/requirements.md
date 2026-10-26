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
