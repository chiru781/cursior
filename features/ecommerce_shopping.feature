Feature: E-commerce Shopping
  As a customer
  I want to browse and purchase products
  So that I can buy items I need

  Background:
    Given I am logged into the application
    And I am on the products page

  @smoke @shopping
  Scenario: Add product to cart and complete purchase
    When I search for "laptop"
    And I select the first product from search results
    And I add the product to cart
    And I proceed to checkout
    And I enter shipping information:
      | address  | 123 Main St        |
      | city     | New York           |
      | state    | NY                 |
      | zip      | 10001              |
      | country  | USA                |
    And I select payment method "Credit Card"
    And I enter payment details:
      | card_number | 4111111111111111 |
      | expiry      | 12/25            |
      | cvv         | 123              |
      | name        | John Doe         |
    And I place the order
    Then I should see order confirmation
    And I should receive order confirmation email
    And the order should be saved in database

  @regression @cart
  Scenario: Cart management operations
    Given I have products in my cart:
      | product     | quantity | price |
      | Laptop      | 1        | 999   |
      | Mouse       | 2        | 25    |
    When I update laptop quantity to 2
    And I remove mouse from cart
    Then cart total should be updated to "$1998"
    And cart should contain only laptop

  @filters @search
  Scenario: Product filtering and sorting
    When I apply filters:
      | category    | Electronics |
      | price_range | 100-500     |
      | brand       | Apple       |
    And I sort by "price_low_to_high"
    Then I should see only filtered products
    And products should be sorted by price ascending
    And filter count should be displayed

  @negative @checkout
  Scenario Outline: Checkout with invalid payment information
    Given I have items in cart
    When I proceed to checkout
    And I enter payment details:
      | card_number | <card>   |
      | expiry      | <expiry> |
      | cvv         | <cvv>    |
    And I place the order
    Then I should see error message "<error>"

    Examples:
      | card             | expiry | cvv | error                        |
      | 1234567890123456 | 12/25  | 123 | Invalid card number          |
      | 4111111111111111 | 12/20  | 123 | Card expired                 |
      | 4111111111111111 | 12/25  | 12  | Invalid CVV                  |

  @inventory @realtime
  Scenario: Real-time inventory updates
    Given product "Limited Edition Watch" has 2 items in stock
    When another user purchases 1 item
    And I refresh the product page
    Then I should see "1 item left in stock"
    When I add the product to cart
    And another user purchases the last item
    And I proceed to checkout
    Then I should see "Item out of stock" error

  @api @integration
  Scenario: Verify order details through API
    Given I have placed an order with order ID "ORD123456"
    When I fetch order details through API
    Then the API should return correct order information
    And order status should be "processing"
    And payment status should be "completed"