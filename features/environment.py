import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from config.config import Config
import allure
from datetime import datetime

def before_all(context):
    """Setup before all tests"""
    context.config_obj = Config()
    context.config_obj.create_directories()
    setup_logging(context)
    
    # Store start time
    context.test_start_time = datetime.now()
    
    logging.info("="*50)
    logging.info("BDD Test Execution Started")
    logging.info(f"Environment: {context.config_obj.ENVIRONMENT}")
    logging.info(f"Browser: {context.config_obj.BROWSER}")
    logging.info(f"Base URL: {context.config_obj.BASE_URL}")
    logging.info("="*50)

def before_feature(context, feature):
    """Setup before each feature"""
    logging.info(f"Starting Feature: {feature.name}")

def before_scenario(context, scenario):
    """Setup before each scenario"""
    logging.info(f"Starting Scenario: {scenario.name}")
    
    # Initialize driver for each scenario
    context.driver = initialize_driver(context.config_obj)
    
    # Set implicit wait
    context.driver.implicitly_wait(context.config_obj.IMPLICIT_WAIT)
    
    # Set page load timeout
    context.driver.set_page_load_timeout(context.config_obj.PAGE_LOAD_TIMEOUT)
    
    # Maximize window if not headless
    if not context.config_obj.HEADLESS:
        context.driver.maximize_window()
    
    # Store scenario start time
    context.scenario_start_time = datetime.now()

def after_step(context, step):
    """After each step"""
    if step.status == "failed":
        logging.error(f"Step failed: {step.name}")
        
        if context.config_obj.TAKE_SCREENSHOTS_ON_FAILURE:
            take_screenshot(context, f"failed_step_{step.name}")

def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    scenario_duration = datetime.now() - context.scenario_start_time
    
    if scenario.status == "failed":
        logging.error(f"Scenario failed: {scenario.name}")
        logging.error(f"Duration: {scenario_duration}")
        
        if context.config_obj.TAKE_SCREENSHOTS_ON_FAILURE:
            take_screenshot(context, f"failed_scenario_{scenario.name}")
    else:
        logging.info(f"Scenario passed: {scenario.name}")
        logging.info(f"Duration: {scenario_duration}")
    
    # Close driver
    if hasattr(context, 'driver') and context.driver:
        try:
            context.driver.quit()
        except Exception as e:
            logging.warning(f"Error closing driver: {e}")

def after_feature(context, feature):
    """Cleanup after each feature"""
    logging.info(f"Finished Feature: {feature.name}")

def after_all(context):
    """Cleanup after all tests"""
    test_duration = datetime.now() - context.test_start_time
    
    logging.info("="*50)
    logging.info("BDD Test Execution Completed")
    logging.info(f"Total Duration: {test_duration}")
    logging.info("="*50)

def initialize_driver(config_obj):
    """Initialize WebDriver based on configuration"""
    browser = config_obj.BROWSER.lower()
    
    try:
        if browser == 'chrome':
            return setup_chrome_driver(config_obj)
        elif browser == 'firefox':
            return setup_firefox_driver(config_obj)
        elif browser == 'edge':
            return setup_edge_driver(config_obj)
        else:
            raise ValueError(f"Unsupported browser: {browser}")
    
    except Exception as e:
        logging.error(f"Failed to initialize {browser} driver: {e}")
        # Fallback to Chrome
        logging.info("Falling back to Chrome driver")
        return setup_chrome_driver(config_obj)

def setup_chrome_driver(config_obj):
    """Setup Chrome WebDriver"""
    chrome_options = webdriver.ChromeOptions()
    
    for option in config_obj.CHROME_OPTIONS:
        chrome_options.add_argument(option)
    
    # Additional Chrome preferences
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2 if config_obj.HEADLESS else 1
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Disable logging
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Setup Chrome service
    service = ChromeService(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    logging.info("Chrome driver initialized successfully")
    
    return driver

def setup_firefox_driver(config_obj):
    """Setup Firefox WebDriver"""
    firefox_options = webdriver.FirefoxOptions()
    
    for option in config_obj.FIREFOX_OPTIONS:
        firefox_options.add_argument(option)
    
    # Firefox preferences
    firefox_options.set_preference("dom.webnotifications.enabled", False)
    firefox_options.set_preference("media.volume_scale", "0.0")
    
    if config_obj.HEADLESS:
        firefox_options.add_argument("--headless")
    
    # Setup Firefox service
    service = FirefoxService(GeckoDriverManager().install())
    
    driver = webdriver.Firefox(service=service, options=firefox_options)
    logging.info("Firefox driver initialized successfully")
    
    return driver

def setup_edge_driver(config_obj):
    """Setup Edge WebDriver"""
    edge_options = webdriver.EdgeOptions()
    
    # Add Edge-specific options
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--no-sandbox")
    
    if config_obj.HEADLESS:
        edge_options.add_argument("--headless")
    
    # Setup Edge service
    service = EdgeService(EdgeChromiumDriverManager().install())
    
    driver = webdriver.Edge(service=service, options=edge_options)
    logging.info("Edge driver initialized successfully")
    
    return driver

def setup_logging(context):
    """Setup logging configuration"""
    config_obj = context.config_obj
    
    # Create logs directory
    os.makedirs(config_obj.LOG_DIR, exist_ok=True)
    
    # Setup logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config_obj.LOG_LEVEL),
        format=log_format,
        handlers=[
            logging.FileHandler(
                os.path.join(config_obj.LOG_DIR, 'test_execution.log'),
                mode='w'
            ),
            logging.StreamHandler()
        ]
    )
    
    # Suppress noisy logs
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

def take_screenshot(context, name):
    """Take screenshot and attach to report"""
    try:
        if hasattr(context, 'driver') and context.driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"{name}_{timestamp}.png"
            screenshot_path = os.path.join(
                context.config_obj.SCREENSHOT_DIR, 
                screenshot_name
            )
            
            # Take screenshot
            context.driver.save_screenshot(screenshot_path)
            logging.info(f"Screenshot saved: {screenshot_path}")
            
            # Attach to Allure report if available
            try:
                with open(screenshot_path, 'rb') as f:
                    allure.attach(
                        f.read(),
                        name=screenshot_name,
                        attachment_type=allure.attachment_type.PNG
                    )
            except:
                pass  # Allure might not be available
                
            return screenshot_path
    
    except Exception as e:
        logging.error(f"Failed to take screenshot: {e}")
        return None

def get_browser_logs(context):
    """Get browser console logs"""
    try:
        if hasattr(context, 'driver') and context.driver:
            logs = context.driver.get_log('browser')
            if logs:
                logging.info("Browser Console Logs:")
                for log in logs:
                    logging.info(f"[{log['level']}] {log['message']}")
            return logs
    except Exception as e:
        logging.warning(f"Could not retrieve browser logs: {e}")
        return []

def cleanup_test_data(context):
    """Cleanup test data created during tests"""
    try:
        # This would include database cleanup, file cleanup, etc.
        # Implementation depends on your specific test data management
        logging.info("Cleaning up test data...")
        
        # Example: Clean up test users, orders, etc.
        if hasattr(context, 'test_users_created'):
            for user_email in context.test_users_created:
                # Clean up user from database
                pass
        
        if hasattr(context, 'test_orders_created'):
            for order_id in context.test_orders_created:
                # Clean up order from database
                pass
                
    except Exception as e:
        logging.error(f"Error during test data cleanup: {e}")

# Hook for custom browser setup based on user data
def setup_custom_browser(context):
    """Setup browser with custom configuration"""
    user_data = context.config.userdata
    
    if 'browser' in user_data:
        context.config_obj.BROWSER = user_data['browser']
    
    if 'headless' in user_data:
        context.config_obj.HEADLESS = user_data['headless'].lower() == 'true'
    
    if 'environment' in user_data:
        context.config_obj.ENVIRONMENT = user_data['environment']
        context.config_obj._load_environment_config()