# ADR-001: Database choice (SQLite)

Status: decided by the team after Call 3.

## The question
Call 2 left the data store as "Technology TBD". Call 3 asked for the choice to be written down next to the load numbers instead of being said in a meeting.

## Options
1. **SQLite** (one file, no server). It handles writes one at a time in a queue.
2. **PostgreSQL** (separate server). Row-level locking, many writers at once, but one more thing to install, run and secure.

## Decision
SQLite, in write-ahead-log (WAL) mode, for version one.

## Load numbers we actually have
- Launch audience: about 26,000 USF students (Call 1 and Call 2).
- Peak: Marcus said "a few hundred people at once in the first minutes, maybe more". Nobody has given a real number. Marcus is trying to get sales data from Darnell's past events. **The peak is still unknown (open item Q13).**
- Design scenario from Call 3: 200 buyers press buy in the same second. This is an example from the call, not a confirmed target.

## Back-of-envelope check (not measured)
If one purchase transaction holds the write lock for about 10 ms (an assumption we have not measured), 200 purchases in one second queue up and the last buyer waits about 2 seconds. Kenji said a short queue is acceptable for launch. We need to measure the real transaction time before trusting this.

## Why SQLite
- Part 2 chose a single modular application because we did not want extra moving parts before there is evidence we need them. A separate database server is the same kind of extra part.
- The ticket check and decrement is one statement (`UPDATE ... SET available = available - :n WHERE event_id = :id AND available >= :n`) inside the purchase transaction. SQLite runs it safely because only one writer runs at a time, so two buyers cannot both take the last ticket.
- Nothing to install for developers or for the TA.

## Consequences and risks
- Writes are serialized, so throughput has a ceiling. If measurements or real traffic show purchases waiting too long, move to PostgreSQL. Only the database layer changes because all SQL sits behind the components.
- The database is one file on one machine. That is fine for version one and rules out running several copies of the application.
- Reads during a write are not blocked in WAL mode, so browsing stays fast while purchases happen.
- We must test the concurrent-purchase case (two buyers, one ticket) as an automated test.

## Update (Part 5): what we measured
`tests_system/test_performance.py` has 20 signed-in buyers each make 5 purchases at the same moment against the real app (Flask development server, one process, SQLite in WAL mode) on a developer sandbox, not a production machine.
- 100 purchases, 0 failures, no oversell, every ticket accounted for.
- Latency of the purchase request: median 22 to 41 ms; **95th percentile 381 to 496 ms** over six repeat runs; slowest single request 570 to 776 ms.
- With 50 buyers (250 purchases) the 95th percentile rose to **about 1,150 ms** and the slowest to 1.9 s.
- This matches the shape the back-of-envelope predicted: writes queue up behind the one writer. It does **not** tell us whether that is good enough, because nobody has said how fast is fast enough (open item Q13, RISK-003). The test judges against a team placeholder of 500 ms at the 95th percentile, which one of the six repeat runs missed by only 4 ms.
- The "200 buyers in one second" scenario from Call 3 has not been run.
