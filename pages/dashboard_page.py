from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class DashboardPage(BasePage):
    """Page Object Model for Dashboard Page"""
    
    # Locators
    WELCOME_MESSAGE = (By.CLASS_NAME, "welcome-message")
    USER_PROFILE = (By.CLASS_NAME, "user-profile")
    LOGOUT_BUTTON = (By.ID, "logoutButton")
    USER_MENU = (By.CLASS_NAME, "user-menu")
    PROFILE_SECTION = (By.CLASS_NAME, "profile-section")
    NAVIGATION_MENU = (By.CLASS_NAME, "nav-menu")
    
    # Alternative locators
    LOGOUT_ALT = (By.XPATH, "//a[contains(text(), 'Logout')]")
    WELCOME_ALT = (By.XPATH, "//*[contains(text(), 'Welcome')]")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def is_page_loaded(self):
        """Check if dashboard page is loaded"""
        try:
            self.wait_for_element_visible(self.WELCOME_MESSAGE, timeout=5)
            return True
        except:
            return "dashboard" in self.get_current_url().lower()
    
    def is_user_logged_in(self):
        """Check if user is logged in"""
        return self.is_element_present(self.USER_PROFILE) or self.is_element_present(self.LOGOUT_BUTTON)
    
    def get_welcome_message(self):
        """Get welcome message text"""
        try:
            return self.get_text(self.WELCOME_MESSAGE)
        except:
            try:
                return self.get_text(self.WELCOME_ALT)
            except:
                return "Welcome message not found"
    
    def is_profile_section_visible(self):
        """Check if profile section is visible"""
        return self.is_element_visible(self.PROFILE_SECTION)
    
    def get_profile_data(self):
        """Get profile data"""
        profile_data = {}
        try:
            # Extract profile information
            profile_section = self.find_element(self.PROFILE_SECTION)
            
            # Get name
            try:
                name_element = profile_section.find_element(By.CLASS_NAME, "user-name")
                profile_data['name'] = name_element.text
            except:
                pass
            
            # Get email
            try:
                email_element = profile_section.find_element(By.CLASS_NAME, "user-email")
                profile_data['email'] = email_element.text
            except:
                pass
            
            # Get auth provider
            try:
                auth_element = profile_section.find_element(By.CLASS_NAME, "auth-provider")
                profile_data['auth_provider'] = auth_element.get_attribute("data-provider")
            except:
                profile_data['auth_provider'] = 'local'
            
        except Exception as e:
            self.logger.warning(f"Could not extract profile data: {e}")
        
        return profile_data
    
    def logout(self):
        """Logout from application"""
        try:
            self.click_element(self.LOGOUT_BUTTON)
        except:
            self.click_element(self.LOGOUT_ALT)