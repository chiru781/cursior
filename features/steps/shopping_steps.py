from behave import given, when, then
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.products_page import ProductsPage
from pages.product_detail_page import ProductDetailPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.dashboard_page import DashboardPage
from utils.database_utils import DatabaseManager
from utils.api_client import APIClient
from utils.email_utils import EmailVerifier
import time

@given('I am logged into the application')
def step_login_to_app(context):
    # Assume user is already logged in or perform login
    dashboard_page = DashboardPage(context.driver)
    if not dashboard_page.is_user_logged_in():
        # Perform login steps
        from pages.login_page import LoginPage
        login_page = LoginPage(context.driver)
        login_page.navigate_to_login()
        login_page.enter_email("test@example.com")
        login_page.enter_password("SecurePass123!")
        login_page.click_login_button()

@given('I am on the products page')
def step_navigate_to_products(context):
    context.products_page = ProductsPage(context.driver)
    context.products_page.navigate_to_products()
    assert context.products_page.is_page_loaded(), "Products page did not load"

@when('I search for "{search_term}"')
def step_search_products(context, search_term):
    context.search_term = search_term
    context.products_page.search_products(search_term)

@when('I select the first product from search results')
def step_select_first_product(context):
    context.product_detail_page = context.products_page.click_first_product()
    assert context.product_detail_page.is_page_loaded(), "Product detail page did not load"

@when('I add the product to cart')
def step_add_to_cart(context):
    context.product_detail_page.add_to_cart()
    # Wait for add to cart confirmation
    context.product_detail_page.wait_for_cart_update()

@when('I proceed to checkout')
def step_proceed_to_checkout(context):
    context.cart_page = CartPage(context.driver)
    context.cart_page.navigate_to_cart()
    context.checkout_page = context.cart_page.proceed_to_checkout()
    assert context.checkout_page.is_page_loaded(), "Checkout page did not load"

@when('I enter shipping information')
def step_enter_shipping_info(context):
    context.shipping_data = {}
    for row in context.table:
        field = row['address'] if 'address' in row.headings else row[0]
        value = row['123 Main St'] if '123 Main St' in row.headings else row[1]
        context.shipping_data[field] = value
        context.checkout_page.enter_shipping_field(field, value)

@when('I select payment method "{payment_method}"')
def step_select_payment_method(context, payment_method):
    context.checkout_page.select_payment_method(payment_method)

@when('I enter payment details')
def step_enter_payment_details(context):
    context.payment_data = {}
    for row in context.table:
        field = row[0]
        value = row[1]
        context.payment_data[field] = value
        context.checkout_page.enter_payment_field(field, value)

@when('I place the order')
def step_place_order(context):
    context.order_confirmation = context.checkout_page.place_order()

@then('I should see order confirmation')
def step_verify_order_confirmation(context):
    assert context.order_confirmation.is_displayed(), "Order confirmation not displayed"
    context.order_id = context.order_confirmation.get_order_id()
    assert context.order_id, "Order ID not found in confirmation"

@then('I should receive order confirmation email')
def step_verify_confirmation_email(context):
    email_verifier = EmailVerifier()
    # Get email from user session or payment data
    user_email = context.payment_data.get('email', 'test@example.com')
    email_received = email_verifier.wait_for_email(
        user_email, 
        subject_contains="Order Confirmation", 
        timeout=30
    )
    assert email_received, f"Order confirmation email not received for {user_email}"

@then('the order should be saved in database')
def step_verify_order_in_database(context):
    db_manager = DatabaseManager()
    order = db_manager.get_order_by_id(context.order_id)
    assert order is not None, f"Order {context.order_id} not found in database"
    assert order['status'] == 'pending' or order['status'] == 'processing'

@given('I have products in my cart')
def step_add_products_to_cart(context):
    context.cart_page = CartPage(context.driver)
    context.cart_page.navigate_to_cart()
    
    # Clear existing cart first
    context.cart_page.clear_cart()
    
    # Add products from table
    for row in context.table:
        product_name = row['product']
        quantity = int(row['quantity'])
        price = float(row['price'])
        
        # Navigate to product and add to cart
        context.products_page = ProductsPage(context.driver)
        context.products_page.navigate_to_products()
        context.products_page.search_products(product_name)
        product_detail = context.products_page.click_first_product()
        product_detail.set_quantity(quantity)
        product_detail.add_to_cart()

@when('I update laptop quantity to {new_quantity:d}')
def step_update_quantity(context, new_quantity):
    context.cart_page.update_product_quantity("Laptop", new_quantity)

@when('I remove mouse from cart')
def step_remove_product(context):
    context.cart_page.remove_product("Mouse")

@then('cart total should be updated to "{expected_total}"')
def step_verify_cart_total(context, expected_total):
    actual_total = context.cart_page.get_cart_total()
    assert actual_total == expected_total, f"Expected total {expected_total}, got {actual_total}"

@then('cart should contain only laptop')
def step_verify_cart_contents(context):
    cart_items = context.cart_page.get_cart_items()
    assert len(cart_items) == 1, f"Expected 1 item in cart, got {len(cart_items)}"
    assert cart_items[0]['name'].lower() == 'laptop', "Cart should contain only laptop"

@when('I apply filters')
def step_apply_filters(context):
    context.filters = {}
    for row in context.table:
        filter_type = row[0]
        filter_value = row[1]
        context.filters[filter_type] = filter_value
        context.products_page.apply_filter(filter_type, filter_value)

@when('I sort by "{sort_option}"')
def step_sort_products(context, sort_option):
    context.products_page.sort_products(sort_option)

@then('I should see only filtered products')
def step_verify_filtered_products(context):
    products = context.products_page.get_displayed_products()
    
    # Verify filters are applied
    for product in products:
        if 'category' in context.filters:
            assert product['category'] == context.filters['category']
        
        if 'price_range' in context.filters:
            price_range = context.filters['price_range'].split('-')
            min_price, max_price = float(price_range[0]), float(price_range[1])
            assert min_price <= product['price'] <= max_price
        
        if 'brand' in context.filters:
            assert product['brand'] == context.filters['brand']

@then('products should be sorted by price ascending')
def step_verify_price_sorting(context):
    products = context.products_page.get_displayed_products()
    prices = [product['price'] for product in products]
    assert prices == sorted(prices), "Products are not sorted by price ascending"

@then('filter count should be displayed')
def step_verify_filter_count(context):
    filter_count = context.products_page.get_filter_count()
    assert filter_count > 0, "Filter count should be displayed"

@given('I have items in cart')
def step_ensure_items_in_cart(context):
    # Add a default item to cart for checkout testing
    context.cart_page = CartPage(context.driver)
    context.cart_page.navigate_to_cart()
    
    if context.cart_page.is_cart_empty():
        # Add a default product
        context.products_page = ProductsPage(context.driver)
        context.products_page.navigate_to_products()
        product_detail = context.products_page.click_first_product()
        product_detail.add_to_cart()

@then('I should see error message "{error}"')
def step_verify_checkout_error(context, error):
    actual_error = context.checkout_page.get_error_message()
    assert error.lower() in actual_error.lower(), \
        f"Expected error '{error}', got '{actual_error}'"

@given('product "{product_name}" has {stock_count:d} items in stock')
def step_set_product_stock(context, product_name, stock_count):
    db_manager = DatabaseManager()
    db_manager.update_product_stock(product_name, stock_count)
    context.initial_stock = stock_count

@when('another user purchases {quantity:d} item')
def step_simulate_concurrent_purchase(context, quantity):
    # Simulate another user purchasing items via API
    api_client = APIClient()
    purchase_data = {
        'product_name': "Limited Edition Watch",
        'quantity': quantity,
        'user_id': 'test_user_2'
    }
    context.concurrent_response = api_client.purchase_product(purchase_data)

@when('I refresh the product page')
def step_refresh_product_page(context):
    context.driver.refresh()
    time.sleep(2)  # Wait for page to load

@then('I should see "{stock_message}" item left in stock')
def step_verify_stock_message(context, stock_message):
    product_detail = ProductDetailPage(context.driver)
    actual_message = product_detail.get_stock_message()
    assert stock_message in actual_message, \
        f"Expected '{stock_message}', got '{actual_message}'"

@when('another user purchases the last item')
def step_purchase_last_item(context):
    api_client = APIClient()
    purchase_data = {
        'product_name': "Limited Edition Watch",
        'quantity': 1,
        'user_id': 'test_user_3'
    }
    context.final_purchase_response = api_client.purchase_product(purchase_data)

@then('I should see "Item out of stock" error')
def step_verify_out_of_stock_error(context):
    error_message = context.checkout_page.get_error_message()
    assert "out of stock" in error_message.lower(), \
        f"Expected out of stock error, got '{error_message}'"

@given('I have placed an order with order ID "{order_id}"')
def step_create_test_order(context, order_id):
    # Create a test order in database
    db_manager = DatabaseManager()
    order_data = {
        'order_id': order_id,
        'user_id': 'test_user_1',
        'status': 'processing',
        'payment_status': 'completed',
        'total_amount': 99.99,
        'created_at': 'NOW()'
    }
    db_manager.create_order(order_data)
    context.test_order_id = order_id

@when('I fetch order details through API')
def step_fetch_order_via_api(context):
    api_client = APIClient()
    context.api_order_response = api_client.get_order_details(context.test_order_id)

@then('the API should return correct order information')
def step_verify_api_order_response(context):
    response = context.api_order_response
    assert response['status_code'] == 200, f"API call failed with status {response['status_code']}"
    assert response['data']['order_id'] == context.test_order_id

@then('order status should be "{expected_status}"')
def step_verify_api_order_status(context, expected_status):
    order_data = context.api_order_response['data']
    assert order_data['status'] == expected_status, \
        f"Expected status '{expected_status}', got '{order_data['status']}'"

@then('payment status should be "{expected_payment_status}"')
def step_verify_api_payment_status(context, expected_payment_status):
    order_data = context.api_order_response['data']
    assert order_data['payment_status'] == expected_payment_status, \
        f"Expected payment status '{expected_payment_status}', got '{order_data['payment_status']}'"