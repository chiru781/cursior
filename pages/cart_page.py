from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class CartPage(BasePage):
    """Page Object Model for Shopping Cart Page"""
    
    # Locators
    CART_ITEMS = (By.CLASS_NAME, "cart-item")
    ITEM_NAME = (By.CLASS_NAME, "item-name")
    ITEM_PRICE = (By.CLASS_NAME, "item-price")
    ITEM_QUANTITY = (By.CLASS_NAME, "item-quantity")
    ITEM_TOTAL = (By.CLASS_NAME, "item-total")
    
    QUANTITY_INPUT = (By.CSS_SELECTOR, "input[name='quantity']")
    UPDATE_QUANTITY = (By.CLASS_NAME, "update-quantity")
    REMOVE_ITEM = (By.CLASS_NAME, "remove-item")
    
    CART_SUBTOTAL = (By.CLASS_NAME, "cart-subtotal")
    CART_TAX = (By.CLASS_NAME, "cart-tax")
    CART_SHIPPING = (By.CLASS_NAME, "cart-shipping")
    CART_TOTAL = (By.CLASS_NAME, "cart-total")
    
    PROCEED_TO_CHECKOUT = (By.ID, "proceedToCheckout")
    CONTINUE_SHOPPING = (By.ID, "continueShopping")
    CLEAR_CART = (By.ID, "clearCart")
    
    EMPTY_CART_MESSAGE = (By.CLASS_NAME, "empty-cart-message")
    
    # Alternative locators
    CHECKOUT_ALT = (By.XPATH, "//button[contains(text(), 'Checkout')]")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def navigate_to_cart(self):
        """Navigate to cart page"""
        cart_url = f"{self.config.BASE_URL}/cart"
        self.navigate_to(cart_url)
        self.wait_for_page_load()
    
    def is_page_loaded(self):
        """Check if cart page is loaded"""
        return "cart" in self.get_current_url().lower()
    
    def is_cart_empty(self):
        """Check if cart is empty"""
        return self.is_element_visible(self.EMPTY_CART_MESSAGE)
    
    def get_cart_items(self):
        """Get list of items in cart"""
        items = []
        cart_item_elements = self.find_elements(self.CART_ITEMS)
        
        for i, item_element in enumerate(cart_item_elements):
            try:
                name = item_element.find_element(By.CLASS_NAME, "item-name").text
                price = item_element.find_element(By.CLASS_NAME, "item-price").text
                quantity_element = item_element.find_element(By.CLASS_NAME, "item-quantity")
                quantity = quantity_element.text if quantity_element.text.isdigit() else 1
                total = item_element.find_element(By.CLASS_NAME, "item-total").text
                
                items.append({
                    'index': i,
                    'name': name,
                    'price': price,
                    'quantity': int(quantity),
                    'total': total,
                    'element': item_element
                })
            except Exception as e:
                self.logger.warning(f"Could not extract details for cart item {i}: {e}")
        
        return items
    
    def get_cart_total(self):
        """Get cart total amount"""
        return self.get_text(self.CART_TOTAL)
    
    def get_cart_subtotal(self):
        """Get cart subtotal"""
        return self.get_text(self.CART_SUBTOTAL)
    
    def get_cart_tax(self):
        """Get cart tax amount"""
        try:
            return self.get_text(self.CART_TAX)
        except:
            return "$0.00"
    
    def get_cart_shipping(self):
        """Get shipping cost"""
        try:
            return self.get_text(self.CART_SHIPPING)
        except:
            return "$0.00"
    
    def update_product_quantity(self, product_name, new_quantity):
        """Update quantity for a specific product"""
        cart_items = self.get_cart_items()
        
        for item in cart_items:
            if product_name.lower() in item['name'].lower():
                item_element = item['element']
                
                # Find quantity input within this item
                try:
                    quantity_input = item_element.find_element(By.CSS_SELECTOR, "input[name='quantity']")
                    quantity_input.clear()
                    quantity_input.send_keys(str(new_quantity))
                    
                    # Click update button if it exists
                    try:
                        update_btn = item_element.find_element(By.CLASS_NAME, "update-quantity")
                        update_btn.click()
                    except:
                        # Auto-update or press enter
                        from selenium.webdriver.common.keys import Keys
                        quantity_input.send_keys(Keys.ENTER)
                    
                    self.wait_for_cart_update()
                    return
                    
                except Exception as e:
                    self.logger.error(f"Failed to update quantity for {product_name}: {e}")
        
        raise Exception(f"Product '{product_name}' not found in cart")
    
    def remove_product(self, product_name):
        """Remove a product from cart"""
        cart_items = self.get_cart_items()
        
        for item in cart_items:
            if product_name.lower() in item['name'].lower():
                item_element = item['element']
                
                try:
                    remove_btn = item_element.find_element(By.CLASS_NAME, "remove-item")
                    remove_btn.click()
                    
                    # Confirm removal if dialog appears
                    try:
                        self.accept_alert()
                    except:
                        pass
                    
                    self.wait_for_cart_update()
                    return
                    
                except Exception as e:
                    self.logger.error(f"Failed to remove {product_name}: {e}")
        
        raise Exception(f"Product '{product_name}' not found in cart")
    
    def clear_cart(self):
        """Clear all items from cart"""
        try:
            self.click_element(self.CLEAR_CART)
            # Confirm if dialog appears
            try:
                self.accept_alert()
            except:
                pass
            self.wait_for_cart_update()
        except:
            # Alternative: remove items one by one
            cart_items = self.get_cart_items()
            for item in cart_items:
                try:
                    remove_btn = item['element'].find_element(By.CLASS_NAME, "remove-item")
                    remove_btn.click()
                    try:
                        self.accept_alert()
                    except:
                        pass
                except:
                    continue
    
    def proceed_to_checkout(self):
        """Proceed to checkout"""
        try:
            self.click_element(self.PROCEED_TO_CHECKOUT)
        except:
            self.click_element(self.CHECKOUT_ALT)
        
        from pages.checkout_page import CheckoutPage
        return CheckoutPage(self.driver)
    
    def continue_shopping(self):
        """Continue shopping (go back to products)"""
        self.click_element(self.CONTINUE_SHOPPING)
        from pages.products_page import ProductsPage
        return ProductsPage(self.driver)
    
    def wait_for_cart_update(self):
        """Wait for cart to update"""
        import time
        time.sleep(2)  # Wait for cart calculations to update