# localization

## Call 7: release 1.5, Spanish via Flask-Babel

- **localization-001** (ubiquitous): The {EventHub} shall provide English and Spanish interface text through Flask-Babel compiled message catalogs.
- **localization-002** (event-driven): When a reader selects Spanish, the {EventHub} shall show translated titles, menus, forms, checkout, order history, administrator pages and web error messages.
- **localization-003** (event-driven): When a reader saves a language choice, the {EventHub} shall use that choice on later pages instead of the configured default or browser language header.
- **localization-004** (event-driven): When a reader has not saved a language choice, the {EventHub} shall use the English or Spanish default from operator configuration rather than an unapproved browser-language rule.
- **localization-005** (event-driven): When a reader uses Spanish, the {EventHub} shall format displayed dates and currency amounts using Flask-Babel locale data without changing stored prices or timestamps.
- **localization-006** (unwanted): If a Spanish message-catalog entry is unavailable, then the {EventHub} shall use the corresponding English message rather than showing a missing key.
- **localization-007** (ubiquitous): The {EventHub} shall store the interface translations in version-controlled message catalogs that are distinct from pricing and purchasing logic.
- **localization-008** (event-driven): When an operator configures an unsupported default language, the {EventHub} shall reject the configuration before serving requests.

## Decision record

English and Spanish are the two release languages. The covered screens are listed in localization-002. For this coursework, source Spanish wording is carried forward from the team's Part 7 translations, which were AI-assisted and have **not** been approved by the customer or a native Spanish reviewer. Reader cookie is higher priority than operator default; Accept-Language does not automatically override the operator default. Choice is stored in a SameSite=Lax cookie using the existing CSRF-protected language form. The selected Spanish locale is es_ES and English is en_US; the student's geographical region remains an open customer decision. These rules are explicit decisions for the prototype, not claims of Darnell's approval.
