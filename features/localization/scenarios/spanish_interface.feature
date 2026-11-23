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

  @localization-009
  Scenario: Each translated UI message has a documented source
    Given the team maintains a version-controlled translation provenance manifest
    When the manifest is checked against both locale catalogs
    Then each key has a source and a review status in both languages

  @localization-010
  Scenario: A language choice uses a protected cookie
    Given the operator has configured Spanish as the default language
    When a reader saves English through the language form
    Then the response sets a protected language cookie

  @localization-011 @localization-012
  Scenario: A translation draft with a changed placeholder is rejected
    Given the team has an external Spanish translation draft
    When a variable name is changed in that draft
    Then the release catalog validation rejects the change
