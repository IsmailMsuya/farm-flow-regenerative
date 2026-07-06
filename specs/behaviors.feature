Feature: Climate-relief review

  Scenario: Rainfall is above the threshold
    Given a complete normal scenario
    When the fixed contract is evaluated
    Then the status is "normal"

  Scenario: Rainfall is low without vegetation confirmation
    Given a complete watchlist scenario
    When the fixed contract is evaluated
    Then the status is "watchlist"

  Scenario: Rainfall and vegetation conditions are met
    Given a complete triggered scenario
    When the fixed contract is evaluated
    Then the status is "triggered_review"
    And human review is required

  Scenario: Rainfall coverage is too low
    Given an incomplete rainfall scenario
    When the fixed contract is evaluated
    Then the status is "insufficient_data"

  Scenario: A payment is requested
    When a user asks the system to send money
    Then the policy gate blocks the request

