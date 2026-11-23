Feature: Pricing requirements from the Part 5 baseline
  @pricing-008
  Scenario: A yen quote is rounded using integer minor units
    Given a ticket costs 125 US cents
    When a three-ticket yen quote is computed
    Then the result is a whole number of yen without a floating-point amount
