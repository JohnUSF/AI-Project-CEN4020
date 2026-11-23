Feature: Inventory requirements from the Part 5 baseline
  @inventory-004
  Scenario: Inventory is never reduced for an oversold request
    Given only one event ticket remains
    When a buyer tries to reserve two tickets
    Then the inventory rejects the request and retains one ticket
