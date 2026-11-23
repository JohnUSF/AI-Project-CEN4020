Feature: Admin requirements from the Part 5 baseline
  @admin-007
  Scenario: An unsupported administrator rate is rejected
    Given an administrator account is available
    When the administrator tries to set a negative exchange rate
    Then the current exchange rate is not changed
