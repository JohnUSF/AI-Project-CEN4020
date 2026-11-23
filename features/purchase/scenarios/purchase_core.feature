Feature: Purchase requirements from the Part 5 baseline
  @purchase-007
  Scenario: Zero ticket quantity is rejected
    Given a purchase quantity of zero was submitted
    When the purchase form quantity is validated
    Then the purchase is rejected with a quantity error
