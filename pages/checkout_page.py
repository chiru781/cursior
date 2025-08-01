from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class CheckoutPage(BasePage):
    """Page Object Model for Checkout Page"""
    
    # Shipping information
    SHIPPING_SECTION = (By.CLASS_NAME, "shipping-section")
    ADDRESS_INPUT = (By.ID, "address")
    CITY_INPUT = (By.ID, "city")
    STATE_INPUT = (By.ID, "state")
    ZIP_INPUT = (By.ID, "zip")
    COUNTRY_INPUT = (By.ID, "country")
    
    # Payment information
    PAYMENT_SECTION = (By.CLASS_NAME, "payment-section")
    PAYMENT_METHOD_DROPDOWN = (By.ID, "paymentMethod")
    CARD_NUMBER_INPUT = (By.ID, "cardNumber")
    EXPIRY_INPUT = (By.ID, "expiry")
    CVV_INPUT = (By.ID, "cvv")
    CARDHOLDER_NAME_INPUT = (By.ID, "cardholderName")
    
    # Order summary
    ORDER_SUMMARY = (By.CLASS_NAME, "order-summary")
    ORDER_TOTAL = (By.CLASS_NAME, "order-total")
    
    # Buttons
    PLACE_ORDER_BUTTON = (By.ID, "placeOrder")
    CONTINUE_SHOPPING_BUTTON = (By.ID, "continueShopping")
    
    # Error and success messages
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "success-message")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def is_page_loaded(self):
        """Check if checkout page is loaded"""
        try:
            self.wait_for_element_visible(self.PLACE_ORDER_BUTTON, timeout=5)
            return True
        except:
            return "checkout" in self.get_current_url().lower()
    
    def enter_shipping_field(self, field_name, value):
        """Enter shipping information"""
        field_mapping = {
            'address': self.ADDRESS_INPUT,
            'city': self.CITY_INPUT,
            'state': self.STATE_INPUT,
            'zip': self.ZIP_INPUT,
            'country': self.COUNTRY_INPUT
        }
        
        if field_name in field_mapping:
            self.enter_text(field_mapping[field_name], value)
        else:
            self.logger.warning(f"Unknown shipping field: {field_name}")
    
    def select_payment_method(self, payment_method):
        """Select payment method"""
        self.select_dropdown_by_text(self.PAYMENT_METHOD_DROPDOWN, payment_method)
    
    def enter_payment_field(self, field_name, value):
        """Enter payment information"""
        field_mapping = {
            'card_number': self.CARD_NUMBER_INPUT,
            'expiry': self.EXPIRY_INPUT,
            'cvv': self.CVV_INPUT,
            'name': self.CARDHOLDER_NAME_INPUT
        }
        
        if field_name in field_mapping:
            self.enter_text(field_mapping[field_name], value)
        else:
            self.logger.warning(f"Unknown payment field: {field_name}")
    
    def place_order(self):
        """Place the order"""
        self.click_element(self.PLACE_ORDER_BUTTON)
        from pages.order_confirmation_page import OrderConfirmationPage
        return OrderConfirmationPage(self.driver)
    
    def get_error_message(self):
        """Get error message"""
        try:
            return self.get_text(self.ERROR_MESSAGE)
        except:
            return "No error message found"

class OrderConfirmationPage(BasePage):
    """Page Object Model for Order Confirmation Page"""
    
    ORDER_ID = (By.CLASS_NAME, "order-id")
    CONFIRMATION_MESSAGE = (By.CLASS_NAME, "confirmation-message")
    ORDER_DETAILS = (By.CLASS_NAME, "order-details")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def is_displayed(self):
        """Check if order confirmation is displayed"""
        return self.is_element_visible(self.CONFIRMATION_MESSAGE)
    
    def get_order_id(self):
        """Get order ID"""
        try:
            order_text = self.get_text(self.ORDER_ID)
            # Extract order ID from text
            import re
            match = re.search(r'[A-Z0-9]{6,}', order_text)
            return match.group() if match else None
        except:
            return None