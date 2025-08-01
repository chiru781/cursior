Feature: User Login
  As a registered user
  I want to login to my account
  So that I can access my personalized dashboard and features

  Background:
    Given I am on the login page

  @smoke @login
  Scenario: Successful login with valid credentials
    When I enter login credentials:
      | email    | test@example.com |
      | password | SecurePass123!   |
    And I click login button
    Then I should be redirected to dashboard
    And I should see welcome message "Welcome back, Test User"
    And I should see my profile information

  @negative @login
  Scenario Outline: Login with invalid credentials
    When I enter login credentials:
      | email    | <email>    |
      | password | <password> |
    And I click login button
    Then I should see error message "<error_message>"
    And I should remain on login page

    Examples:
      | email              | password     | error_message              |
      | invalid@email.com  | SecurePass123!| Invalid email or password  |
      | test@example.com   | wrongpass    | Invalid email or password  |
      |                    | SecurePass123!| Email is required         |
      | test@example.com   |              | Password is required       |

  @security @login
  Scenario: Account lockout after multiple failed attempts
    Given I have attempted login 4 times with wrong password
    When I enter login credentials:
      | email    | test@example.com |
      | password | wrongpassword    |
    And I click login button
    Then I should see error message "Account temporarily locked"
    And the account should be locked for 15 minutes

  @regression @login
  Scenario: Remember me functionality
    When I enter valid login credentials
    And I check "Remember me" checkbox
    And I click login button
    And I logout
    And I close the browser
    And I reopen the browser and visit login page
    Then I should be automatically logged in

  @social @login
  Scenario: Social media login with Google
    When I click "Login with Google" button
    And I authorize the application on Google
    Then I should be redirected to dashboard
    And my profile should be populated with Google data