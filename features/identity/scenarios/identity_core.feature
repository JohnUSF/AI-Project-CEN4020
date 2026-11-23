Feature: Identity requirements from the Part 5 baseline
  @identity-005
  Scenario: A failed login does not reveal account existence
    Given a registered buyer account exists
    When a wrong password and an unknown email are submitted
    Then both attempts return the same invalid credentials error
