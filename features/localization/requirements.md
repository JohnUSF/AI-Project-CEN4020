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

- **localization-009** (ubiquitous): The {EventHub} shall identify the source and review status of every English and Spanish interface text entry in a version-controlled translation provenance manifest.
- **localization-010** (event-driven): When a reader saves a supported language through the language form, the {EventHub} shall preserve the choice in an HttpOnly SameSite=Lax cookie after validating the CSRF token.
- **localization-011** (ubiquitous): The {EventHub} shall preserve the same named substitution placeholders in corresponding English and Spanish catalog messages.
- **localization-012** (event-driven): When a team member prepares a translation update from an external draft, the {EventHub} shall reject a catalog update with missing keys or mismatched named placeholders before release.

## Decision record

English and Spanish are the two release languages. The covered screens are listed in localization-002. For this coursework, source Spanish wording is carried forward from the team's Part 7 translations, which were AI-assisted and have **not** been approved by the customer or a native Spanish reviewer. Reader cookie is higher priority than operator default; Accept-Language does not automatically override the operator default. Choice is stored in a SameSite=Lax cookie using the existing CSRF-protected language form. The selected Spanish locale is es_ES and English is en_US; the student's geographical region remains an open customer decision. These rules are explicit decisions for the prototype, not claims of Darnell's approval.

**Translation ownership and source:** The initial English wording comes from the team's earlier application UI. The Spanish wording is a team-produced, AI-assisted draft adapted from Part 7; it is not represented as a certified translation or as approved by Darnell. The manifest records this honestly for each key. External spreadsheet drafts are inputs only; the reviewed, versioned gettext catalogs are the release source.
