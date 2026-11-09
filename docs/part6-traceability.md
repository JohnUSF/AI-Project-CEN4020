# Call 6: requirement -> design -> code -> tests

This supplements the earlier `docs/part5-traceability.md`; none of the earlier requirement IDs have been deleted or rewritten.

| Call 6 evidence / expectation | EARS IDs | Responsible files | Test proof |
|---|---|---|---|
| Correct minor units for all currencies; yen cannot be divided by 100 as a display cleanup | pricing-018, pricing-020 | `eventhub/pricing.py` (unchanged calculation), `eventhub/i18n.py` (presentation only) | `tests/test_call6_maintenance.py::test_real_purchase_persists_exact_currency_total`, `test_exact_price_every_supported_currency`; optional `tests_system/test_call6_browser.py` |
| Administrator updates currency rate then a new buyer purchase sees it; old order retains original rate | admin-009, pricing-010 | `eventhub/admin.py`, `eventhub/purchase.py`, existing `rates` database | `test_admin_rate_change_is_used_by_next_purchase_not_previous`, optional `test_admin_web_rate_change_then_next_yen_order_uses_new_rate` |
| Spanish UI and regional money/date display | system-010/011, pricing-019 | `locales/en.json`, `locales/es.json`, `eventhub/i18n.py`, `eventhub/web.py`, templates, JS | `test_spanish_strings_and_fallback_without_changing_events`, optional HTTP/browser tests |
| Monitor unusually low/high charged orders using original rate and create a reviewable alert | audit-009/010/011 | `eventhub/monitor.py`, `eventhub/db.py`, `scripts/check_order_anomalies.py`, admin templates | `test_undercharge_generates_one_durable_alert_without_repeating`, `test_admin_acknowledgement_keeps_alert_history`, optional `test_admin_alert_page_requires_role_and_can_acknowledge` |
| Consistent WAL backup, checksum and guarded offline restore | system-012/013 | `eventhub/backups.py`, backup/restore scripts | `test_online_backup_integrity_and_guarded_restore` |

**Operational notes:** Running tests is not proof of a staffed alert rotation, offsite backup policy, real production rollback or customer translation approval. Call 6 deliberately leaves those items unresolved; they are in Q22–Q26 and RISK-006–010.
