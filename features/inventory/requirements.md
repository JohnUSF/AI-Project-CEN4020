# inventory

## Ticket counts

- **inventory-001** (ubiquitous): The {EventHub} shall never sell more tickets than exist, even when several purchase requests are processed at the same time.
- **inventory-002** (ubiquitous): The {EventHub} shall keep one authoritative ticket count for each event in its database.
- **inventory-003** (event-driven): When a purchase is executed, the {EventHub} shall check that enough tickets are available and reduce the ticket count as a single indivisible step.
- **inventory-004** (unwanted): If a purchase would take a ticket count below zero, then the {EventHub} shall reject the purchase and leave the ticket count unchanged.
- **inventory-005** (state-driven): While a buyer is completing checkout, the {EventHub} shall not reserve or hold the selected tickets [TBD: Q5 hold or no hold is still pending].
