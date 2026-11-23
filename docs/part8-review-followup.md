# Part 8 - reviewed corrections and disposition

Original read-only pinned review: Part 5 `cc73d4f5` -> Part 8 `4f037f3`; skill SHA `301b02b12bff98e4688e6984af6556802322bbde` in Copilot Fusion. Corrections: developer commit `dbebb63`. As reported by Jai, both teammates approved the following decisions; the sentences below summarize their reasoning rather than reproducing chat quotations.

| Finding | Jai decision | John decision | Implementation |
|---|---|---|---|
| SQLite restore could collide with stale WAL/SHM files | **accepted** - This can affect a restored database, so I kept the fail-closed check and regression tests. | **accepted** - The restore needs to be safe before we submit, and the two sidecar tests make this easier to check. | Offline WAL/SHM rejection and two regression cases |
| SMTP could authenticate when STARTTLS was off | **accepted** - We should not let the notifier send credentials without encryption; I kept the STARTTLS guard. | **accepted** - I agree with rejecting insecure SMTP settings instead of silently sending a login. | Require STARTTLS before SMTP login and regression case |
| Seven English strings bypassed the translation catalogs | **accepted** - These strings should go through the same catalog as the rest of the interface, without changing old English wording. | **accepted** - The catalog fix is small and tested, and it helps us avoid missing translations later. | Seven English template strings moved into gettext and regression case |
| English yen display uses JPY 4,500 instead of the native yen symbol | **rejected** - I want to keep the older English display test stable until the customer confirms the format change. | **rejected** - I agree this should be a separate reviewed change because it alters the established receipt display contract. | No change; preserved documented English compatibility until customer requirement approved |


See `docs/part8-review-record.md` for the official five-check/required-severity format, the complete three lists, and Kenji's safeguards. This review approved only the proposed technical decisions, not a production release or customer locale policy.
