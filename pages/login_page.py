from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config.config import Config

class LoginPage(BasePage):
    """Page Object Model for Login Page"""
    
    # Locators
    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "loginButton")
    REMEMBER_ME_CHECKBOX = (By.ID, "rememberMe")
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgot Password?")
    GOOGLE_LOGIN_BUTTON = (By.ID, "googleLogin")
    FACEBOOK_LOGIN_BUTTON = (By.ID, "facebookLogin")
    REGISTER_LINK = (By.LINK_TEXT, "Create Account")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "success-message")
    LOADING_SPINNER = (By.CLASS_NAME, "loading-spinner")
    
    # Alternative locators
    EMAIL_ALT = (By.NAME, "email")
    PASSWORD_ALT = (By.NAME, "password")
    LOGIN_ALT = (By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign In')]")
    REMEMBER_ALT = (By.NAME, "remember")
    GOOGLE_ALT = (By.XPATH, "//button[contains(text(), 'Google')]")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.config = Config()
    
    def navigate_to_login(self):
        """Navigate to login page"""
        login_url = f"{self.config.BASE_URL}/login"
        self.navigate_to(login_url)
        self.wait_for_page_load()
    
    def is_page_loaded(self):
        """Check if login page is loaded"""
        try:
            self.wait_for_element_visible(self.LOGIN_BUTTON, timeout=5)
            return True
        except:
            try:
                self.wait_for_element_visible(self.LOGIN_ALT, timeout=2)
                return True
            except:
                return False
    
    def enter_email(self, email):
        """Enter email address"""
        try:
            self.enter_text(self.EMAIL_INPUT, email)
        except:
            self.enter_text(self.EMAIL_ALT, email)
    
    def enter_password(self, password):
        """Enter password"""
        try:
            self.enter_text(self.PASSWORD_INPUT, password)
        except:
            self.enter_text(self.PASSWORD_ALT, password)
    
    def click_login_button(self):
        """Click login button"""
        try:
            self.click_element(self.LOGIN_BUTTON)
        except:
            self.click_element(self.LOGIN_ALT)
        
        self.wait_for_loading_to_complete()
    
    def check_remember_me(self):
        """Check remember me checkbox"""
        try:
            if not self.is_element_selected(self.REMEMBER_ME_CHECKBOX):
                self.click_element(self.REMEMBER_ME_CHECKBOX)
        except:
            if not self.is_element_selected(self.REMEMBER_ALT):
                self.click_element(self.REMEMBER_ALT)
    
    def click_forgot_password(self):
        """Click forgot password link"""
        self.click_element(self.FORGOT_PASSWORD_LINK)
    
    def click_google_login(self):
        """Click Google login button"""
        try:
            self.click_element(self.GOOGLE_LOGIN_BUTTON)
        except:
            self.click_element(self.GOOGLE_ALT)
    
    def click_facebook_login(self):
        """Click Facebook login button"""
        self.click_element(self.FACEBOOK_LOGIN_BUTTON)
    
    def click_register_link(self):
        """Click register/create account link"""
        self.click_element(self.REGISTER_LINK)
    
    def get_error_message(self):
        """Get error message text"""
        try:
            return self.get_text(self.ERROR_MESSAGE)
        except:
            error_selectors = [
                (By.CLASS_NAME, "alert-danger"),
                (By.CLASS_NAME, "error"),
                (By.XPATH, "//*[contains(@class, 'error')]"),
                (By.XPATH, "//*[contains(text(), 'Invalid') or contains(text(), 'incorrect')]")
            ]
            
            for selector in error_selectors:
                try:
                    return self.get_text(selector)
                except:
                    continue
            
            return "Error message not found"
    
    def get_success_message(self):
        """Get success message text"""
        try:
            return self.get_text(self.SUCCESS_MESSAGE)
        except:
            return "Success message not found"
    
    def login(self, email, password, remember_me=False):
        """Complete login process"""
        self.enter_email(email)
        self.enter_password(password)
        
        if remember_me:
            self.check_remember_me()
        
        self.click_login_button()
    
    def is_element_selected(self, locator):
        """Check if checkbox is selected"""
        element = self.find_element(locator)
        return element.is_selected()
    
    def wait_for_loading_to_complete(self):
        """Wait for loading to complete"""
        try:
            self.wait_for_element_visible(self.LOADING_SPINNER, timeout=2)
            self.wait_for_element_invisible(self.LOADING_SPINNER, timeout=10)
        except:
            pass
    
    def wait_for_element_invisible(self, locator, timeout=10):
        """Wait for element to become invisible"""
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.invisibility_of_element_located(locator))
        except:
            pass
    
    def handle_google_oauth(self):
        """Handle Google OAuth flow (simplified for testing)"""
        # In real scenario, this would handle actual Google OAuth
        # For testing, we simulate the flow
        original_window = self.driver.current_window_handle
        
        # Wait for Google OAuth page to load
        self.wait_for_page_load()
        
        # Simulate OAuth approval (in real test, use test Google account)
        if "accounts.google.com" in self.get_current_url():
            # This would normally interact with Google's OAuth interface
            # For demo purposes, we'll simulate successful OAuth
            self.logger.info("Simulating Google OAuth approval")
            
            # In real implementation, you would:
            # 1. Enter test Google credentials
            # 2. Grant permissions
            # 3. Wait for redirect back to application
        
        # Switch back to original window if needed
        if len(self.get_window_handles()) > 1:
            self.switch_to_window(original_window)
    
    def clear_login_form(self):
        """Clear login form fields"""
        try:
            self.find_element(self.EMAIL_INPUT, timeout=2).clear()
        except:
            pass
        
        try:
            self.find_element(self.PASSWORD_INPUT, timeout=2).clear()
        except:
            pass