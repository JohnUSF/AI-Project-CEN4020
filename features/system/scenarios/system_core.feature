Feature: System requirements from the Part 5 baseline
  @system-002
  Scenario: Invalid incoming language is refused
    Given a reader has a valid form session
    When the reader submits an unsupported language
    Then the HTTP request is rejected without saving a language cookie
