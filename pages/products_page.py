from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pages.base_page import BasePage
from pages.product_detail_page import ProductDetailPage
from config.config import Config

class ProductsPage(BasePage):
    """Page Object Model for Products Page"""
    
    # Locators
    SEARCH_BOX = (By.ID, "searchBox")
    SEARCH_BUTTON = (By.ID, "searchButton")
    PRODUCT_ITEMS = (By.CLASS_NAME, "product-item")
    PRODUCT_TITLES = (By.CLASS_NAME, "product-title")
    PRODUCT_PRICES = (By.CLASS_NAME, "product-price")
    PRODUCT_IMAGES = (By.CLASS_NAME, "product-image")
    
    # Filter elements
    CATEGORY_FILTER = (By.ID, "categoryFilter")
    PRICE_FILTER = (By.ID, "priceFilter")
    BRAND_FILTER = (By.ID, "brandFilter")
    RATING_FILTER = (By.ID, "ratingFilter")
    FILTER_APPLY_BUTTON = (By.ID, "applyFilters")
    FILTER_CLEAR_BUTTON = (By.ID, "clearFilters")
    FILTER_COUNT = (By.CLASS_NAME, "filter-count")
    
    # Sort elements
    SORT_DROPDOWN = (By.ID, "sortBy")
    SORT_OPTIONS = (By.CSS_SELECTOR, "#sortBy option")
    
    # Pagination
    PAGINATION_NEXT = (By.CLASS_NAME, "pagination-next")
    PAGINATION_PREV = (By.CLASS_NAME, "pagination-prev")
    PAGINATION_NUMBERS = (By.CLASS_NAME, "pagination-number")
    
    # Cart related
    ADD_TO_CART_BUTTONS = (By.CLASS_NAME, "add-to-cart")
    CART_ICON = (By.ID, "cartIcon")
    CART_COUNT = (By.CLASS_NAME, "cart-count")
    
    # Loading and messages
    LOADING_SPINNER = (By.CLASS_NAME, "loading-spinner")
    NO_RESULTS_MESSAGE = (By.CLASS_NAME, "no-results")
    
    # Alternative locators
    SEARCH_ALT = (By.NAME, "search")
    PRODUCT_ALT = (By.CSS_SELECTOR, ".product, .item")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.config = Config()
    
    def navigate_to_products(self):
        """Navigate to products page"""
        products_url = f"{self.config.BASE_URL}/products"
        self.navigate_to(products_url)
        self.wait_for_page_load()
    
    def is_page_loaded(self):
        """Check if products page is loaded"""
        try:
            self.wait_for_element_visible(self.SEARCH_BOX, timeout=5)
            return True
        except:
            return "products" in self.get_current_url().lower()
    
    def search_products(self, search_term):
        """Search for products"""
        try:
            search_box = self.find_element(self.SEARCH_BOX)
            search_box.clear()
            search_box.send_keys(search_term)
            search_box.send_keys(Keys.ENTER)
        except:
            # Try alternative search method
            try:
                self.enter_text(self.SEARCH_ALT, search_term)
                self.click_element(self.SEARCH_BUTTON)
            except:
                # Fallback: type and press enter
                search_box = self.find_element(self.SEARCH_ALT)
                search_box.send_keys(search_term)
                search_box.send_keys(Keys.ENTER)
        
        self.wait_for_search_results()
    
    def wait_for_search_results(self):
        """Wait for search results to load"""
        try:
            # Wait for loading spinner to appear and disappear
            self.wait_for_element_visible(self.LOADING_SPINNER, timeout=2)
            self.wait_for_element_invisible(self.LOADING_SPINNER, timeout=10)
        except:
            pass
        
        # Wait for products to be visible
        self.wait_for_element_visible(self.PRODUCT_ITEMS, timeout=10)
    
    def get_product_count(self):
        """Get number of products displayed"""
        products = self.find_elements(self.PRODUCT_ITEMS)
        return len(products)
    
    def get_displayed_products(self):
        """Get list of displayed products with details"""
        products = []
        product_elements = self.find_elements(self.PRODUCT_ITEMS)
        
        for i, product in enumerate(product_elements):
            try:
                # Get product details
                title_element = product.find_element(By.CLASS_NAME, "product-title")
                price_element = product.find_element(By.CLASS_NAME, "product-price")
                
                title = title_element.text
                price_text = price_element.text
                price = self.extract_price_from_text(price_text)
                
                # Try to get additional details
                try:
                    category_element = product.find_element(By.CLASS_NAME, "product-category")
                    category = category_element.text
                except:
                    category = "Unknown"
                
                try:
                    brand_element = product.find_element(By.CLASS_NAME, "product-brand")
                    brand = brand_element.text
                except:
                    brand = "Unknown"
                
                products.append({
                    'index': i,
                    'title': title,
                    'price': price,
                    'price_text': price_text,
                    'category': category,
                    'brand': brand,
                    'element': product
                })
            except Exception as e:
                self.logger.warning(f"Could not extract details for product {i}: {e}")
        
        return products
    
    def extract_price_from_text(self, price_text):
        """Extract numeric price from price text"""
        import re
        # Extract number from text like "$123.45" or "£99.99"
        match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if match:
            return float(match.group())
        return 0.0
    
    def click_first_product(self):
        """Click on the first product"""
        products = self.find_elements(self.PRODUCT_ITEMS)
        if products:
            products[0].click()
            return ProductDetailPage(self.driver)
        else:
            raise Exception("No products found to click")
    
    def click_product_by_index(self, index):
        """Click on product by index"""
        products = self.find_elements(self.PRODUCT_ITEMS)
        if index < len(products):
            products[index].click()
            return ProductDetailPage(self.driver)
        else:
            raise Exception(f"Product at index {index} not found")
    
    def click_product_by_title(self, title):
        """Click on product by title"""
        products = self.get_displayed_products()
        for product in products:
            if title.lower() in product['title'].lower():
                product['element'].click()
                return ProductDetailPage(self.driver)
        
        raise Exception(f"Product with title '{title}' not found")
    
    def apply_filter(self, filter_type, filter_value):
        """Apply a filter"""
        filter_mapping = {
            'category': self.CATEGORY_FILTER,
            'price_range': self.PRICE_FILTER,
            'brand': self.BRAND_FILTER,
            'rating': self.RATING_FILTER
        }
        
        if filter_type in filter_mapping:
            filter_element = filter_mapping[filter_type]
            self.select_dropdown_by_text(filter_element, filter_value)
            
            # Apply filters if there's an apply button
            try:
                self.click_element(self.FILTER_APPLY_BUTTON)
                self.wait_for_search_results()
            except:
                # Auto-apply filter
                self.wait_for_search_results()
        else:
            raise Exception(f"Unknown filter type: {filter_type}")
    
    def clear_filters(self):
        """Clear all applied filters"""
        try:
            self.click_element(self.FILTER_CLEAR_BUTTON)
            self.wait_for_search_results()
        except:
            self.logger.warning("Clear filters button not found")
    
    def sort_products(self, sort_option):
        """Sort products by given option"""
        sort_mapping = {
            'price_low_to_high': 'Price: Low to High',
            'price_high_to_low': 'Price: High to Low',
            'name_a_to_z': 'Name: A to Z',
            'name_z_to_a': 'Name: Z to A',
            'newest': 'Newest First',
            'rating': 'Highest Rated'
        }
        
        sort_text = sort_mapping.get(sort_option, sort_option)
        self.select_dropdown_by_text(self.SORT_DROPDOWN, sort_text)
        self.wait_for_search_results()
    
    def get_filter_count(self):
        """Get number of active filters"""
        try:
            count_text = self.get_text(self.FILTER_COUNT)
            # Extract number from text like "3 filters applied"
            import re
            match = re.search(r'\d+', count_text)
            return int(match.group()) if match else 0
        except:
            return 0
    
    def add_product_to_cart_by_index(self, index):
        """Add product to cart by index from product list"""
        add_to_cart_buttons = self.find_elements(self.ADD_TO_CART_BUTTONS)
        if index < len(add_to_cart_buttons):
            add_to_cart_buttons[index].click()
            self.wait_for_cart_update()
        else:
            raise Exception(f"Add to cart button at index {index} not found")
    
    def wait_for_cart_update(self):
        """Wait for cart count to update"""
        try:
            # Wait for cart animation or count update
            import time
            time.sleep(1)
        except:
            pass
    
    def get_cart_count(self):
        """Get current cart item count"""
        try:
            return int(self.get_text(self.CART_COUNT))
        except:
            return 0
    
    def go_to_cart(self):
        """Navigate to shopping cart"""
        self.click_element(self.CART_ICON)
        from pages.cart_page import CartPage
        return CartPage(self.driver)
    
    def go_to_next_page(self):
        """Go to next page of products"""
        self.click_element(self.PAGINATION_NEXT)
        self.wait_for_search_results()
    
    def go_to_previous_page(self):
        """Go to previous page of products"""
        self.click_element(self.PAGINATION_PREV)
        self.wait_for_search_results()
    
    def go_to_page(self, page_number):
        """Go to specific page number"""
        page_links = self.find_elements(self.PAGINATION_NUMBERS)
        for link in page_links:
            if link.text == str(page_number):
                link.click()
                self.wait_for_search_results()
                return
        
        raise Exception(f"Page {page_number} not found")
    
    def is_no_results_displayed(self):
        """Check if no results message is displayed"""
        return self.is_element_visible(self.NO_RESULTS_MESSAGE)
    
    def wait_for_element_invisible(self, locator, timeout=10):
        """Wait for element to become invisible"""
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.invisibility_of_element_located(locator))
        except:
            pass