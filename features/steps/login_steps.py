from behave import given, when, then
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utils.database_utils import DatabaseManager
from utils.security_utils import SecurityManager
import time

@given('I am on the login page')
def step_navigate_to_login(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.navigate_to_login()
    assert context.login_page.is_page_loaded(), "Login page did not load"

@when('I enter login credentials')
def step_enter_login_credentials(context):
    context.login_data = {}
    for row in context.table:
        field = row[0]  # email or password
        value = row[1]
        context.login_data[field] = value
        if field == 'email':
            context.login_page.enter_email(value)
        elif field == 'password':
            context.login_page.enter_password(value)

@when('I enter valid login credentials')
def step_enter_valid_credentials(context):
    context.login_page.enter_email("test@example.com")
    context.login_page.enter_password("SecurePass123!")

@when('I click login button')
def step_click_login(context):
    context.login_page.click_login_button()

@when('I check "Remember me" checkbox')
def step_check_remember_me(context):
    context.login_page.check_remember_me()

@when('I logout')
def step_logout(context):
    dashboard_page = DashboardPage(context.driver)
    dashboard_page.logout()

@when('I close the browser')
def step_close_browser(context):
    context.driver.quit()

@when('I reopen the browser and visit login page')
def step_reopen_browser(context):
    # Reinitialize driver and visit login page
    from features.environment import initialize_driver
    context.driver = initialize_driver(context.config.userdata.get('browser', 'chrome'))
    context.login_page = LoginPage(context.driver)
    context.login_page.navigate_to_login()

@when('I click "Login with Google" button')
def step_click_google_login(context):
    context.login_page.click_google_login()

@when('I authorize the application on Google')
def step_authorize_google(context):
    # Handle Google OAuth flow
    WebDriverWait(context.driver, 10).until(
        lambda driver: "accounts.google.com" in driver.current_url
    )
    # Simulate Google authorization (in real scenario, use test Google account)
    context.login_page.handle_google_oauth()

@then('I should be redirected to dashboard')
def step_verify_dashboard_redirect(context):
    WebDriverWait(context.driver, 10).until(
        lambda driver: "dashboard" in driver.current_url.lower()
    )
    dashboard_page = DashboardPage(context.driver)
    assert dashboard_page.is_page_loaded(), "Dashboard page did not load"

@then('I should see welcome message "{message}"')
def step_verify_welcome_message(context, message):
    dashboard_page = DashboardPage(context.driver)
    actual_message = dashboard_page.get_welcome_message()
    assert message in actual_message, f"Expected '{message}' in welcome message, got '{actual_message}'"

@then('I should see my profile information')
def step_verify_profile_info(context):
    dashboard_page = DashboardPage(context.driver)
    assert dashboard_page.is_profile_section_visible(), "Profile section is not visible"

@then('I should see error message "{error_message}"')
def step_verify_login_error(context, error_message):
    actual_error = context.login_page.get_error_message()
    assert error_message.lower() in actual_error.lower(), \
        f"Expected error '{error_message}', but got '{actual_error}'"

@then('I should remain on login page')
def step_verify_remain_on_login(context):
    assert context.login_page.is_page_loaded(), "Should remain on login page after failed login"

@given('I have attempted login {attempts:d} times with wrong password')
def step_failed_login_attempts(context, attempts):
    context.failed_attempts_email = "test@example.com"
    for i in range(attempts):
        context.login_page.enter_email(context.failed_attempts_email)
        context.login_page.enter_password("wrongpassword")
        context.login_page.click_login_button()
        time.sleep(1)  # Brief pause between attempts

@then('the account should be locked for {minutes:d} minutes')
def step_verify_account_lockout(context, minutes):
    db_manager = DatabaseManager()
    security_manager = SecurityManager()
    
    # Check if account is locked in database
    lockout_info = security_manager.get_lockout_info(context.failed_attempts_email)
    assert lockout_info['is_locked'] == True, "Account should be locked"
    assert lockout_info['lockout_duration'] == minutes, f"Lockout should be {minutes} minutes"

@then('I should be automatically logged in')
def step_verify_auto_login(context):
    # Check if redirected to dashboard without manual login
    current_url = context.driver.current_url
    assert "dashboard" in current_url.lower(), "Should be automatically logged in to dashboard"

@then('my profile should be populated with Google data')
def step_verify_google_profile_data(context):
    dashboard_page = DashboardPage(context.driver)
    profile_data = dashboard_page.get_profile_data()
    
    # Verify that profile contains Google-specific data
    assert profile_data.get('auth_provider') == 'google', "Auth provider should be Google"
    assert profile_data.get('email'), "Email should be populated from Google"
    assert profile_data.get('name'), "Name should be populated from Google"