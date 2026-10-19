# identity

## Accounts and sign-in

- **identity-001** (ubiquitous): The {EventHub} shall allow any person, from any country, to register an account using a name, an email address, and a password.
- **identity-002** (ubiquitous): The {EventHub} shall store every password as a salted hash and shall never store or transmit a password in plaintext.
- **identity-003** (event-driven): When an account is registered with an email address ending in "@usf.edu", the {EventHub} shall apply the USF student discount [TBD: Q1 discount amount, Q2 discount scope] to that account. superseded by pricing-002
- **identity-004** (event-driven): When an account is registered with an email address that does not end in "@usf.edu", the {EventHub} shall apply the standard, non-discounted price to that account. superseded by pricing-003
- **identity-005** (unwanted): If a login attempt uses an incorrect password, then the {EventHub} shall reject the login and display an "invalid credentials" message that does not reveal whether the email address or the password was wrong.
- **identity-006** (state-driven): While a buyer's session has expired, the {EventHub} shall require the buyer to sign in again before granting access to checkout or order history.
- **identity-007** (ubiquitous): The {EventHub} shall require an active, signed-in session to access checkout and order history.
- **identity-008** (event-driven): When a registered person submits a correct email address and password, the {EventHub} shall start a signed-in session for that account.
- **identity-009** (event-driven): When a signed-in person signs out, the {EventHub} shall end that person's session.

## Signed-out access to checkout and order history

- **identity-010** (unwanted): If a visitor who is not signed in requests a checkout page or an order history page, then the {EventHub} shall redirect the visitor to the login page, including when the address was pasted directly into the browser.
- **identity-011** (unwanted): If a visitor who is not signed in requests a checkout page or an order history page, then the {EventHub} shall show no content from that page before the visitor has signed in.
- **identity-012** (unwanted): If a visitor who is not signed in requests a checkout page or an order history page, then the {EventHub} shall create no order record and no checkout record.
- **identity-013** (event-driven): When a visitor signs in after being redirected from a checkout page or an order history page, the {EventHub} shall return the visitor to the page originally requested.
- **identity-014** (ubiquitous): The {EventHub} shall return a visitor only to addresses inside EventHub after sign-in and shall ignore any other return address supplied with the sign-in request.

## Roles

- **identity-015** (ubiquitous): The {EventHub} shall give every account created through registration the buyer role and no other role.
- **identity-016** (ubiquitous): The {EventHub} shall grant the administrator role only through a command run on the server by an operator and shall provide no registration, sign-in, or website action that grants it.
