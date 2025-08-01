Feature: User Registration
  As a new customer
  I want to register for an account
  So that I can access personalized features and make purchases

  Background:
    Given I am on the registration page

  @smoke @registration
  Scenario: Successful user registration with valid data
    When I enter valid registration details:
      | field          | value                    |
      | first_name     | John                     |
      | last_name      | Doe                      |
      | email          | john.doe@example.com     |
      | password       | SecurePass123!           |
      | confirm_password| SecurePass123!          |
      | phone          | +1234567890              |
    And I accept terms and conditions
    And I click register button
    Then I should see registration success message
    And I should receive a welcome email
    And I should be redirected to dashboard

  @negative @registration
  Scenario Outline: Registration with invalid data
    When I enter registration details:
      | field          | value      |
      | first_name     | <first>    |
      | last_name      | <last>     |
      | email          | <email>    |
      | password       | <password> |
      | confirm_password| <confirm> |
    And I click register button
    Then I should see error message "<error_message>"

    Examples:
      | first | last | email              | password    | confirm     | error_message                    |
      |       | Doe  | john@example.com   | Pass123!    | Pass123!    | First name is required           |
      | John  |      | john@example.com   | Pass123!    | Pass123!    | Last name is required            |
      | John  | Doe  | invalid-email      | Pass123!    | Pass123!    | Please enter a valid email       |
      | John  | Doe  | john@example.com   | 123         | 123         | Password must be at least 8 chars|
      | John  | Doe  | john@example.com   | Pass123!    | Pass124!    | Passwords do not match           |

  @regression
  Scenario: Registration with existing email
    Given a user with email "existing@example.com" already exists
    When I enter registration details:
      | field     | value                |
      | first_name| Jane                 |
      | last_name | Smith                |
      | email     | existing@example.com |
      | password  | NewPass123!          |
    And I click register button
    Then I should see error message "Email already exists"

  @api @registration
  Scenario: Verify registration through API
    When I register a new user through API with valid data
    Then the user should be created in the database
    And the user status should be "active"
    And a welcome email should be queued