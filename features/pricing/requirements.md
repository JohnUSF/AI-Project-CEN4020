# pricing

## Currency and discount

- **pricing-001** (ubiquitous): The {EventHub} shall accept a currency selection only from its server-side list of supported currencies [TBD: Q7 final currency list] and shall reject any other currency value, whatever the client submits.
- **pricing-002** (state-driven): While an account's email address ends in "@usf.edu", the {EventHub} shall apply the USF student discount [TBD: Q1 discount amount, Q2 discount scope] to every order placed by that account. superseded by pricing-011
  supersedes: identity-003
- **pricing-003** (state-driven): While an account's email address does not end in "@usf.edu", the {EventHub} shall charge the standard, non-discounted price for every order placed by that account.
  supersedes: identity-004
- **pricing-004** (event-driven): When a discount applies to an order paid in a currency other than US dollars, the {EventHub} shall apply the discount and the currency conversion in the order set by [TBD: Q8 order of operations], and shall round the final charged amount to the smallest unit of the target currency.
- **pricing-005** (ubiquitous): The {EventHub} shall convert and display ticket prices using exchange rates stored in a static configuration file inside EventHub and shall use no external live-rate provider. superseded by pricing-009
- **pricing-006** (event-driven): When a buyer selects a currency, the {EventHub} shall display ticket prices in that currency and charge the order in that currency.

## One place for price logic and how money is held

- **pricing-007** (ubiquitous): The {EventHub} shall compute the base price, quantity total, discount eligibility, and currency conversion of every displayed or charged price in a single place, so that a change to a pricing rule takes effect everywhere at once.
- **pricing-008** (ubiquitous): The {EventHub} shall hold every monetary amount as a whole number of the currency's smallest unit and shall use no floating-point arithmetic for money.

## Exchange rates

- **pricing-009** (ubiquitous): The {EventHub} shall convert and display ticket prices using the exchange rates stored in its database and shall use no external live-rate provider.
  supersedes: pricing-005
- **pricing-010** (event-driven): When an exchange rate is changed, the {EventHub} shall apply the new rate to every price computed after the change.

## Call 4: testable discount eligibility and provisional email rules

- **pricing-011** (state-driven): While an account email has the exact domain "@usf.edu" after case normalization, the {EventHub} shall treat the account as eligible for the USF student discount [TBD: Q1 discount amount and Q2 discount scope].
  supersedes: pricing-002
- **pricing-012** (ubiquitous): The {EventHub} shall trim and case-normalize account email addresses before the dedicated discount eligibility function compares their domains.
- **pricing-013** (event-driven): When an account email has a plus-tagged local part and the exact domain "@usf.edu", the {EventHub} shall treat the account as eligible under the documented provisional email policy [ASSUMPTION: Q17 customer confirmation pending].
- **pricing-014** (event-driven): When an account email belongs to a subdomain such as "@mail.usf.edu", the {EventHub} shall treat the account as ineligible under the documented provisional email policy [ASSUMPTION: Q17 customer confirmation pending].
