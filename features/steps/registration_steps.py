from behave import given, when, then, step
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.registration_page import RegistrationPage
from pages.dashboard_page import DashboardPage
from utils.email_utils import EmailVerifier
from utils.database_utils import DatabaseManager
from utils.api_client import APIClient
from faker import Faker
import time

fake = Faker()

@given('I am on the registration page')
def step_navigate_to_registration(context):
    context.registration_page = RegistrationPage(context.driver)
    context.registration_page.navigate_to_registration()
    assert context.registration_page.is_page_loaded(), "Registration page did not load"

@when('I enter valid registration details')
def step_enter_valid_registration_details(context):
    context.user_data = {}
    for row in context.table:
        field = row['field']
        value = row['value']
        context.user_data[field] = value
        context.registration_page.enter_field(field, value)

@when('I enter registration details')
def step_enter_registration_details(context):
    context.user_data = {}
    for row in context.table:
        field = row['field']
        value = row['value']
        if value:  # Only enter non-empty values
            context.user_data[field] = value
            context.registration_page.enter_field(field, value)

@when('I accept terms and conditions')
def step_accept_terms(context):
    context.registration_page.accept_terms_and_conditions()

@when('I click register button')
def step_click_register(context):
    context.registration_page.click_register_button()

@then('I should see registration success message')
def step_verify_success_message(context):
    success_message = context.registration_page.get_success_message()
    assert "successful" in success_message.lower(), f"Expected success message, got: {success_message}"

@then('I should receive a welcome email')
def step_verify_welcome_email(context):
    email_verifier = EmailVerifier()
    email = context.user_data.get('email')
    # Wait for email to be sent (max 30 seconds)
    email_received = email_verifier.wait_for_email(email, subject_contains="Welcome", timeout=30)
    assert email_received, f"Welcome email not received for {email}"

@then('I should be redirected to dashboard')
def step_verify_redirect_to_dashboard(context):
    dashboard_page = DashboardPage(context.driver)
    WebDriverWait(context.driver, 10).until(
        lambda driver: "dashboard" in driver.current_url.lower()
    )
    assert dashboard_page.is_page_loaded(), "Dashboard page did not load after registration"

@then('I should see error message "{error_message}"')
def step_verify_error_message(context, error_message):
    actual_error = context.registration_page.get_error_message()
    assert error_message.lower() in actual_error.lower(), \
        f"Expected error '{error_message}', but got '{actual_error}'"

@given('a user with email "{email}" already exists')
def step_create_existing_user(context, email):
    # Create user in database for testing duplicate email scenario
    db_manager = DatabaseManager()
    user_data = {
        'email': email,
        'first_name': 'Existing',
        'last_name': 'User',
        'password': 'hashedpassword123',
        'created_at': 'NOW()'
    }
    db_manager.create_user(user_data)
    context.existing_email = email

@when('I register a new user through API with valid data')
def step_register_user_via_api(context):
    api_client = APIClient()
    context.api_user_data = {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.email(),
        'password': 'APITest123!',
        'phone': fake.phone_number()
    }
    context.api_response = api_client.register_user(context.api_user_data)

@then('the user should be created in the database')
def step_verify_user_in_database(context):
    db_manager = DatabaseManager()
    user = db_manager.get_user_by_email(context.api_user_data['email'])
    assert user is not None, "User was not created in database"
    assert user['first_name'] == context.api_user_data['first_name']
    assert user['email'] == context.api_user_data['email']

@then('the user status should be "{expected_status}"')
def step_verify_user_status(context, expected_status):
    db_manager = DatabaseManager()
    user = db_manager.get_user_by_email(context.api_user_data['email'])
    assert user['status'] == expected_status, \
        f"Expected status '{expected_status}', got '{user['status']}'"

@then('a welcome email should be queued')
def step_verify_email_queued(context):
    # Check email queue (assuming Redis or similar message queue)
    from utils.queue_manager import QueueManager
    queue_manager = QueueManager()
    email_jobs = queue_manager.get_email_jobs()
    
    welcome_email_found = False
    for job in email_jobs:
        if (job.get('recipient') == context.api_user_data['email'] and 
            'welcome' in job.get('template', '').lower()):
            welcome_email_found = True
            break
    
    assert welcome_email_found, "Welcome email was not queued"