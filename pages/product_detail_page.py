from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class ProductDetailPage(BasePage):
    """Page Object Model for Product Detail Page"""
    
    # Locators
    PRODUCT_TITLE = (By.CLASS_NAME, "product-title")
    PRODUCT_PRICE = (By.CLASS_NAME, "product-price")
    PRODUCT_DESCRIPTION = (By.CLASS_NAME, "product-description")
    PRODUCT_IMAGE = (By.CLASS_NAME, "product-image")
    STOCK_STATUS = (By.CLASS_NAME, "stock-status")
    STOCK_MESSAGE = (By.CLASS_NAME, "stock-message")
    
    QUANTITY_INPUT = (By.ID, "quantity")
    QUANTITY_PLUS = (By.CLASS_NAME, "quantity-plus")
    QUANTITY_MINUS = (By.CLASS_NAME, "quantity-minus")
    
    ADD_TO_CART_BUTTON = (By.ID, "addToCart")
    BUY_NOW_BUTTON = (By.ID, "buyNow")
    ADD_TO_WISHLIST = (By.ID, "addToWishlist")
    
    PRODUCT_REVIEWS = (By.CLASS_NAME, "product-reviews")
    REVIEW_COUNT = (By.CLASS_NAME, "review-count")
    RATING_STARS = (By.CLASS_NAME, "rating-stars")
    
    # Alternative locators
    ADD_TO_CART_ALT = (By.XPATH, "//button[contains(text(), 'Add to Cart')]")
    QUANTITY_ALT = (By.NAME, "quantity")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def is_page_loaded(self):
        """Check if product detail page is loaded"""
        try:
            self.wait_for_element_visible(self.PRODUCT_TITLE, timeout=5)
            self.wait_for_element_visible(self.ADD_TO_CART_BUTTON, timeout=5)
            return True
        except:
            return False
    
    def get_product_title(self):
        """Get product title"""
        return self.get_text(self.PRODUCT_TITLE)
    
    def get_product_price(self):
        """Get product price"""
        return self.get_text(self.PRODUCT_PRICE)
    
    def get_product_description(self):
        """Get product description"""
        return self.get_text(self.PRODUCT_DESCRIPTION)
    
    def get_stock_status(self):
        """Get stock status"""
        try:
            return self.get_text(self.STOCK_STATUS)
        except:
            return "Unknown"
    
    def get_stock_message(self):
        """Get stock message"""
        try:
            return self.get_text(self.STOCK_MESSAGE)
        except:
            return "Stock information not available"
    
    def is_in_stock(self):
        """Check if product is in stock"""
        stock_status = self.get_stock_status().lower()
        return "in stock" in stock_status or "available" in stock_status
    
    def get_quantity(self):
        """Get current quantity value"""
        try:
            return int(self.get_attribute(self.QUANTITY_INPUT, "value"))
        except:
            return 1
    
    def set_quantity(self, quantity):
        """Set product quantity"""
        try:
            self.enter_text(self.QUANTITY_INPUT, str(quantity))
        except:
            self.enter_text(self.QUANTITY_ALT, str(quantity))
    
    def increase_quantity(self):
        """Increase quantity by 1"""
        self.click_element(self.QUANTITY_PLUS)
    
    def decrease_quantity(self):
        """Decrease quantity by 1"""
        self.click_element(self.QUANTITY_MINUS)
    
    def add_to_cart(self):
        """Add product to cart"""
        try:
            self.click_element(self.ADD_TO_CART_BUTTON)
        except:
            self.click_element(self.ADD_TO_CART_ALT)
    
    def buy_now(self):
        """Click buy now button"""
        self.click_element(self.BUY_NOW_BUTTON)
        # This might redirect to checkout
        from pages.checkout_page import CheckoutPage
        return CheckoutPage(self.driver)
    
    def add_to_wishlist(self):
        """Add product to wishlist"""
        self.click_element(self.ADD_TO_WISHLIST)
    
    def wait_for_cart_update(self):
        """Wait for cart to update after adding item"""
        import time
        time.sleep(2)  # Wait for cart update animation
    
    def get_review_count(self):
        """Get number of reviews"""
        try:
            review_text = self.get_text(self.REVIEW_COUNT)
            import re
            match = re.search(r'\d+', review_text)
            return int(match.group()) if match else 0
        except:
            return 0
    
    def get_rating(self):
        """Get product rating"""
        try:
            rating_element = self.find_element(self.RATING_STARS)
            # Extract rating from element (could be data attribute or class)
            rating = rating_element.get_attribute("data-rating")
            if rating:
                return float(rating)
            
            # Alternative: count filled stars
            filled_stars = rating_element.find_elements(By.CLASS_NAME, "star-filled")
            return len(filled_stars)
        except:
            return 0.0