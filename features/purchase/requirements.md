# purchase

## Quick-buy and checkout

- **purchase-001** (complex): While a buyer is signed in, when the buyer double-clicks an event card, the {EventHub} shall purchase one ticket to that event at once, using the buyer's saved account settings.
- **purchase-002** (unwanted): If a double-click quick-buy cannot be completed, then the {EventHub} shall display an error message that names the cause and return the buyer to the event page (for example, a sold-out event).
- **purchase-003** (event-driven): When a visitor who is not signed in double-clicks an event card, the {EventHub} shall redirect the visitor to the login page and create no order and no checkout record [TBD: Q15 where the visitor lands after signing in].
- **purchase-004** (event-driven): When a buyer submits a quantity and a currency for an event at checkout, the {EventHub} shall execute the purchase and, on success, create one order for that buyer.
- **purchase-005** (event-driven): When a purchase is executed, the {EventHub} shall confirm that the buyer is signed in, the quantity is valid, the event exists, and the currency is supported before it changes any ticket count.

## Limits and validation

- **purchase-006** (unwanted): If the tickets a buyer is purchasing are no longer available at the moment the purchase is executed, then the {EventHub} shall reject the purchase and display a "sold out" message.
- **purchase-007** (unwanted): If a submitted ticket quantity is zero, negative, or above the purchase limit, then the {EventHub} shall reject the order and display an error message specific to the quantity.
- **purchase-008** (ubiquitous): The {EventHub} shall enforce a maximum of [TBD: Q6 cap number] tickets per account per event.
- **purchase-009** (optional): Where an account is verified as a recognized student organization [TBD: Q6 verification process], the {EventHub} shall allow that account to exceed the standard per-account purchase limit.
- **purchase-010** (ubiquitous): The {EventHub} shall validate the ticket quantity on the server for every purchase request, whatever validation the browser performs.
- **purchase-011** (unwanted): If a purchase attempt fails, then the {EventHub} shall display a failure reason specific to its cause, such as "sold out," "invalid quantity," or "unsupported currency," that can be told apart from every other failure reason.
- **purchase-012** (ubiquitous): The {EventHub} shall simulate the payment step in this version and shall integrate no live payment processor.

## Confirmation and order history

- **purchase-013** (event-driven): When a purchase completes successfully, the {EventHub} shall display an on-screen order confirmation showing the event, quantity, currency, exchange rate applied, and total.
- **purchase-014** (ubiquitous): The {EventHub} shall use on-screen order confirmation only in version one and shall not require an order-confirmation email service.
- **purchase-015** (ubiquitous): The {EventHub} shall prevent screenshots of the order confirmation page.
- **purchase-016** (ubiquitous): The {EventHub} shall allow a signed-in buyer to view a list of all of that buyer's past orders.
- **purchase-017** (event-driven): When a buyer opens a past order from order history, the {EventHub} shall display that order's event, quantity, currency paid, exchange rate applied, and total.
- **purchase-018** (ubiquitous): The {EventHub} shall provide door staff a way to verify that a ticket confirmation has not already been used for entry [TBD: Q10 check-in mechanism undefined].
- **purchase-019** (ubiquitous): The {EventHub} shall keep the currency, exchange rate applied, and total of each order unchanged after the order is created.

## Abandoned checkouts

- **purchase-020** (event-driven): When a buyer starts checkout, the {EventHub} shall create no order and change no ticket count until the simulated payment step succeeds.
- **purchase-021** (event-driven): When a buyer cancels checkout, the {EventHub} shall record the checkout as abandoned in the audit log.
- **purchase-022** (event-driven): When a buyer leaves the checkout page without completing the purchase, the {EventHub} shall record the checkout as abandoned in the audit log.
- **purchase-023** (ubiquitous): The {EventHub} shall not disable the browser's Back button and shall not prevent a buyer from closing the tab during checkout.
