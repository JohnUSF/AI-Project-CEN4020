# ADR-003: Where exchange rates live (database table)

Status: decided by the team after Call 3. Replaces the Part 2 decision to keep rates in a static file.

## What changed
Call 2: rates are a file edited by hand about once a semester. Call 3: finance says rates change monthly, maybe weekly. Editing a file and re-releasing the application each time "is not workable"; they want a screen where they sign in and change the number.

## Options
1. **Database table**, edited from the administrator area. Every change is written to the audit log.
2. **Keep a file**, and have the administrator screen rewrite it.

## Decision
A table in the SQLite database owned by the pricing component. The administrator area changes it through pricing, never directly.

## Why
- A database write is part of the same transaction machinery as everything else. A file write is not, so a crash could leave a half-written rates file.
- The audit log can record who changed which rate from what value to what value, and when (requirement audit-004).
- Orders keep the rate that was applied, so history is not affected by later changes.

## Consequences
- The "Configuration & Setup Files" container now holds event setup data, the supported-currency list with digits per currency, the first rates (seed only, loaded once), and settings such as the session idle timeout.
- Changing rates now needs an **administrator**, which is a second kind of human actor. The context diagram goes from one actor to two (see ADR-004).
- Requirement pricing-005 (static file) is superseded by pricing-009 (database).
- Still open: who actually holds the administrator role at EventHub (Marcus said "finance staff, I assume. Or us"). This is a people decision, not a design one (Q14).
