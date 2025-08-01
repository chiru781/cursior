from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config.config import Config

class RegistrationPage(BasePage):
    """Page Object Model for Registration Page"""
    
    # Locators
    FIRST_NAME_INPUT = (By.ID, "firstName")
    LAST_NAME_INPUT = (By.ID, "lastName")
    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    CONFIRM_PASSWORD_INPUT = (By.ID, "confirmPassword")
    PHONE_INPUT = (By.ID, "phone")
    TERMS_CHECKBOX = (By.ID, "termsAndConditions")
    REGISTER_BUTTON = (By.ID, "registerButton")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "success-message")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")
    LOADING_SPINNER = (By.CLASS_NAME, "loading-spinner")
    
    # Alternative locators (in case IDs are not available)
    FIRST_NAME_ALT = (By.NAME, "first_name")
    LAST_NAME_ALT = (By.NAME, "last_name")
    EMAIL_ALT = (By.NAME, "email")
    PASSWORD_ALT = (By.NAME, "password")
    CONFIRM_PASSWORD_ALT = (By.NAME, "confirm_password")
    PHONE_ALT = (By.NAME, "phone")
    TERMS_ALT = (By.NAME, "terms")
    REGISTER_ALT = (By.XPATH, "//button[contains(text(), 'Register')]")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.config = Config()
    
    def navigate_to_registration(self):
        """Navigate to registration page"""
        registration_url = f"{self.config.BASE_URL}/register"
        self.navigate_to(registration_url)
        self.wait_for_page_load()
    
    def is_page_loaded(self):
        """Check if registration page is loaded"""
        try:
            self.wait_for_element_visible(self.REGISTER_BUTTON, timeout=5)
            return True
        except:
            # Try alternative locator
            try:
                self.wait_for_element_visible(self.REGISTER_ALT, timeout=2)
                return True
            except:
                return False
    
    def enter_first_name(self, first_name):
        """Enter first name"""
        try:
            self.enter_text(self.FIRST_NAME_INPUT, first_name)
        except:
            self.enter_text(self.FIRST_NAME_ALT, first_name)
    
    def enter_last_name(self, last_name):
        """Enter last name"""
        try:
            self.enter_text(self.LAST_NAME_INPUT, last_name)
        except:
            self.enter_text(self.LAST_NAME_ALT, last_name)
    
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
    
    def enter_confirm_password(self, confirm_password):
        """Enter confirm password"""
        try:
            self.enter_text(self.CONFIRM_PASSWORD_INPUT, confirm_password)
        except:
            self.enter_text(self.CONFIRM_PASSWORD_ALT, confirm_password)
    
    def enter_phone(self, phone):
        """Enter phone number"""
        try:
            self.enter_text(self.PHONE_INPUT, phone)
        except:
            self.enter_text(self.PHONE_ALT, phone)
    
    def accept_terms_and_conditions(self):
        """Accept terms and conditions"""
        try:
            if not self.is_element_selected(self.TERMS_CHECKBOX):
                self.click_element(self.TERMS_CHECKBOX)
        except:
            if not self.is_element_selected(self.TERMS_ALT):
                self.click_element(self.TERMS_ALT)
    
    def click_register_button(self):
        """Click register button"""
        try:
            self.click_element(self.REGISTER_BUTTON)
        except:
            self.click_element(self.REGISTER_ALT)
        
        # Wait for loading spinner to disappear (if present)
        self.wait_for_loading_to_complete()
    
    def wait_for_loading_to_complete(self):
        """Wait for loading spinner to disappear"""
        try:
            # Wait for spinner to appear (max 2 seconds)
            self.wait_for_element_visible(self.LOADING_SPINNER, timeout=2)
            # Then wait for it to disappear
            self.wait_for_element_invisible(self.LOADING_SPINNER, timeout=10)
        except:
            # Spinner might not appear, continue
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
    
    def is_element_selected(self, locator):
        """Check if checkbox/radio button is selected"""
        element = self.find_element(locator)
        return element.is_selected()
    
    def get_success_message(self):
        """Get success message text"""
        try:
            return self.get_text(self.SUCCESS_MESSAGE)
        except:
            # Look for alternative success indicators
            success_selectors = [
                (By.CLASS_NAME, "alert-success"),
                (By.CLASS_NAME, "success"),
                (By.XPATH, "//*[contains(@class, 'success')]"),
                (By.XPATH, "//*[contains(text(), 'successful')]")
            ]
            
            for selector in success_selectors:
                try:
                    return self.get_text(selector)
                except:
                    continue
            
            return "Success message not found"
    
    def get_error_message(self):
        """Get error message text"""
        try:
            return self.get_text(self.ERROR_MESSAGE)
        except:
            # Look for alternative error indicators
            error_selectors = [
                (By.CLASS_NAME, "alert-danger"),
                (By.CLASS_NAME, "error"),
                (By.CLASS_NAME, "field-error"),
                (By.XPATH, "//*[contains(@class, 'error')]"),
                (By.XPATH, "//*[contains(@class, 'danger')]")
            ]
            
            for selector in error_selectors:
                try:
                    return self.get_text(selector)
                except:
                    continue
            
            return "Error message not found"
    
    def enter_field(self, field_name, value):
        """Generic method to enter data into any field"""
        field_mapping = {
            'first_name': self.enter_first_name,
            'last_name': self.enter_last_name,
            'email': self.enter_email,
            'password': self.enter_password,
            'confirm_password': self.enter_confirm_password,
            'phone': self.enter_phone
        }
        
        if field_name in field_mapping:
            field_mapping[field_name](value)
        else:
            self.logger.warning(f"Unknown field: {field_name}")
    
    def fill_registration_form(self, user_data):
        """Fill complete registration form"""
        if 'first_name' in user_data:
            self.enter_first_name(user_data['first_name'])
        
        if 'last_name' in user_data:
            self.enter_last_name(user_data['last_name'])
        
        if 'email' in user_data:
            self.enter_email(user_data['email'])
        
        if 'password' in user_data:
            self.enter_password(user_data['password'])
        
        if 'confirm_password' in user_data:
            self.enter_confirm_password(user_data['confirm_password'])
        
        if 'phone' in user_data:
            self.enter_phone(user_data['phone'])
    
    def register_user(self, user_data, accept_terms=True):
        """Complete registration process"""
        self.fill_registration_form(user_data)
        
        if accept_terms:
            self.accept_terms_and_conditions()
        
        self.click_register_button()
    
    def get_field_error(self, field_name):
        """Get specific field error message"""
        field_error_locators = {
            'first_name': (By.ID, "firstName-error"),
            'last_name': (By.ID, "lastName-error"),
            'email': (By.ID, "email-error"),
            'password': (By.ID, "password-error"),
            'confirm_password': (By.ID, "confirmPassword-error"),
            'phone': (By.ID, "phone-error")
        }
        
        if field_name in field_error_locators:
            try:
                return self.get_text(field_error_locators[field_name])
            except:
                # Try generic error locator near field
                generic_locator = (By.XPATH, f"//input[@id='{field_name}']/..//span[@class='error']")
                try:
                    return self.get_text(generic_locator)
                except:
                    return "Field error not found"
        
        return "Unknown field"
    
    def clear_all_fields(self):
        """Clear all form fields"""
        fields = [
            self.FIRST_NAME_INPUT,
            self.LAST_NAME_INPUT,
            self.EMAIL_INPUT,
            self.PASSWORD_INPUT,
            self.CONFIRM_PASSWORD_INPUT,
            self.PHONE_INPUT
        ]
        
        for field in fields:
            try:
                element = self.find_element(field, timeout=2)
                element.clear()
            except:
                continue