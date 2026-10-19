# catalog

## Browsing and search

- **catalog-001** (ubiquitous): The {EventHub} shall allow any visitor, signed in or not, to browse the list of available events.
- **catalog-002** (event-driven): When a visitor enters a search term, the {EventHub} shall list the events whose artist name matches the term.
- **catalog-003** (event-driven): When a visitor enters a search term, the {EventHub} shall list the events whose venue name matches the term.
- **catalog-004** (event-driven): When a visitor single-clicks an event card, the {EventHub} shall open that event's detail page.
- **catalog-005** (ubiquitous): The {EventHub} shall display, for each event, the number of tickets currently available [TBD: Q9 meaning of real-time].
- **catalog-006** (ubiquitous): The {EventHub} shall load event records for version one from a setup data file and shall provide no administrator screen for entering events.

## Search with no result

- **catalog-007** (unwanted): If a search matches no events, then the {EventHub} shall show a message that no events match the search, followed by the full list of events.
- **catalog-008** (ubiquitous): The {EventHub} shall display any search text that it repeats back to the visitor as plain text and never as markup.
