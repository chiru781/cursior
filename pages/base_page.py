from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time

class BasePage:
    """Base page class containing common functionality for all pages"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.long_wait = WebDriverWait(driver, 30)
        self.logger = logging.getLogger(__name__)
    
    def navigate_to(self, url):
        """Navigate to a specific URL"""
        self.driver.get(url)
        self.logger.info(f"Navigated to: {url}")
    
    def get_current_url(self):
        """Get current URL"""
        return self.driver.current_url
    
    def get_page_title(self):
        """Get page title"""
        return self.driver.title
    
    def find_element(self, locator, timeout=10):
        """Find a single element with explicit wait"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located(locator))
            return element
        except TimeoutException:
            self.logger.error(f"Element not found: {locator}")
            raise
    
    def find_elements(self, locator, timeout=10):
        """Find multiple elements with explicit wait"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            elements = wait.until(EC.presence_of_all_elements_located(locator))
            return elements
        except TimeoutException:
            self.logger.error(f"Elements not found: {locator}")
            return []
    
    def wait_for_element_clickable(self, locator, timeout=10):
        """Wait for element to be clickable"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            self.logger.error(f"Element not clickable: {locator}")
            raise
    
    def wait_for_element_visible(self, locator, timeout=10):
        """Wait for element to be visible"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            self.logger.error(f"Element not visible: {locator}")
            raise
    
    def wait_for_text_in_element(self, locator, text, timeout=10):
        """Wait for specific text to appear in element"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.text_to_be_present_in_element(locator, text))
        except TimeoutException:
            self.logger.error(f"Text '{text}' not found in element: {locator}")
            return False
    
    def click_element(self, locator, timeout=10):
        """Click an element with wait"""
        element = self.wait_for_element_clickable(locator, timeout)
        try:
            element.click()
            self.logger.info(f"Clicked element: {locator}")
        except Exception as e:
            # Try JavaScript click if regular click fails
            self.driver.execute_script("arguments[0].click();", element)
            self.logger.info(f"Clicked element using JavaScript: {locator}")
    
    def enter_text(self, locator, text, timeout=10, clear_first=True):
        """Enter text into an element"""
        element = self.wait_for_element_visible(locator, timeout)
        if clear_first:
            element.clear()
        element.send_keys(text)
        self.logger.info(f"Entered text '{text}' into element: {locator}")
    
    def get_text(self, locator, timeout=10):
        """Get text from an element"""
        element = self.wait_for_element_visible(locator, timeout)
        text = element.text
        self.logger.info(f"Got text '{text}' from element: {locator}")
        return text
    
    def get_attribute(self, locator, attribute, timeout=10):
        """Get attribute value from an element"""
        element = self.find_element(locator, timeout)
        value = element.get_attribute(attribute)
        self.logger.info(f"Got attribute '{attribute}' = '{value}' from element: {locator}")
        return value
    
    def is_element_present(self, locator, timeout=2):
        """Check if element is present"""
        try:
            self.find_element(locator, timeout)
            return True
        except TimeoutException:
            return False
    
    def is_element_visible(self, locator, timeout=2):
        """Check if element is visible"""
        try:
            self.wait_for_element_visible(locator, timeout)
            return True
        except TimeoutException:
            return False
    
    def scroll_to_element(self, locator):
        """Scroll to a specific element"""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Brief pause for scrolling
    
    def hover_over_element(self, locator):
        """Hover over an element"""
        element = self.find_element(locator)
        ActionChains(self.driver).move_to_element(element).perform()
        self.logger.info(f"Hovered over element: {locator}")
    
    def select_dropdown_by_text(self, locator, text):
        """Select dropdown option by visible text"""
        element = self.find_element(locator)
        select = Select(element)
        select.select_by_visible_text(text)
        self.logger.info(f"Selected '{text}' from dropdown: {locator}")
    
    def select_dropdown_by_value(self, locator, value):
        """Select dropdown option by value"""
        element = self.find_element(locator)
        select = Select(element)
        select.select_by_value(value)
        self.logger.info(f"Selected value '{value}' from dropdown: {locator}")
    
    def wait_for_page_load(self, timeout=30):
        """Wait for page to load completely"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            self.logger.info("Page loaded completely")
        except TimeoutException:
            self.logger.warning("Page load timeout")
    
    def switch_to_frame(self, frame_locator):
        """Switch to iframe"""
        frame = self.find_element(frame_locator)
        self.driver.switch_to.frame(frame)
        self.logger.info(f"Switched to frame: {frame_locator}")
    
    def switch_to_default_content(self):
        """Switch back to default content"""
        self.driver.switch_to.default_content()
        self.logger.info("Switched to default content")
    
    def switch_to_window(self, window_handle):
        """Switch to a specific window"""
        self.driver.switch_to.window(window_handle)
        self.logger.info(f"Switched to window: {window_handle}")
    
    def get_window_handles(self):
        """Get all window handles"""
        return self.driver.window_handles
    
    def take_screenshot(self, filename):
        """Take a screenshot"""
        screenshot_path = f"screenshots/{filename}.png"
        self.driver.save_screenshot(screenshot_path)
        self.logger.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path
    
    def execute_javascript(self, script, *args):
        """Execute JavaScript"""
        result = self.driver.execute_script(script, *args)
        self.logger.info(f"Executed JavaScript: {script}")
        return result
    
    def refresh_page(self):
        """Refresh the current page"""
        self.driver.refresh()
        self.logger.info("Page refreshed")
    
    def go_back(self):
        """Go back to previous page"""
        self.driver.back()
        self.logger.info("Navigated back")
    
    def go_forward(self):
        """Go forward to next page"""
        self.driver.forward()
        self.logger.info("Navigated forward")
    
    def accept_alert(self):
        """Accept JavaScript alert"""
        alert = self.driver.switch_to.alert
        alert.accept()
        self.logger.info("Alert accepted")
    
    def dismiss_alert(self):
        """Dismiss JavaScript alert"""
        alert = self.driver.switch_to.alert
        alert.dismiss()
        self.logger.info("Alert dismissed")
    
    def get_alert_text(self):
        """Get text from JavaScript alert"""
        alert = self.driver.switch_to.alert
        text = alert.text
        self.logger.info(f"Alert text: {text}")
        return text