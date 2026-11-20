Feature: Spanish interface through Flask-Babel
  @localization-001 @localization-002 @localization-007
  Scenario: Spanish text comes from a compiled message catalog
    Given the operator has configured Spanish as the default language
    When a reader visits the home page
    Then the home page has a Spanish title and Spanish navigation

  @localization-003 @localization-004
  Scenario: Explicit language selection takes precedence
    Given the operator has configured Spanish as the default language
    When the reader explicitly switches to English
    Then the site remains in English on the next page

  @localization-005
  Scenario: Spanish formatting keeps yen as an integer without decimals
    Given an order total of 4500 minor yen units
    When the amount is displayed using the Spanish locale
    Then it is displayed without a fraction

  @localization-006
  Scenario: Unknown translation keys fall back instead of disappearing
    Given the Spanish catalog is missing a translated message
    When that English message is displayed
    Then the reader sees English instead of a missing key

  @localization-008
  Scenario: Bad operator language is rejected
    Given the operator configured an unsupported language
    When the application starts
    Then startup is rejected with a configuration error
