Feature: Audit requirements from the Part 5 baseline
  @audit-004
  Scenario: An administrator rate change is audited
    Given an administrator account is available
    When the administrator changes the EUR exchange rate
    Then an audit record contains the rate change
