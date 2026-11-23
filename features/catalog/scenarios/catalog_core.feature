Feature: Catalog requirements from the Part 5 baseline
  @catalog-007
  Scenario: A search without matches shows all events
    Given the event catalog contains seeded events
    When a search term matches no event
    Then the search reports no matches and offers the full list
