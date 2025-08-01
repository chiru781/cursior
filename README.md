# BDD Selenium Automation Framework

A comprehensive Behavior Driven Development (BDD) automation framework using Python, Selenium, and Behave for real-time e-commerce project testing.

## 🚀 Features

- **BDD Framework**: Uses Behave for Gherkin-style test scenarios
- **Page Object Model**: Organized and maintainable page objects
- **Cross-Browser Support**: Chrome, Firefox, Edge
- **Parallel Execution**: Run tests in parallel for faster execution
- **API Testing**: Integrated REST API testing capabilities
- **Database Integration**: Support for PostgreSQL, MySQL, SQLite
- **Email Testing**: Email verification functionality
- **Comprehensive Reporting**: Allure reports with screenshots
- **CI/CD Ready**: Easy integration with Jenkins, GitHub Actions
- **Configurable**: Environment-based configuration management

## 📁 Project Structure

```
bdd-selenium-framework/
├── features/                   # BDD feature files
│   ├── steps/                 # Step definitions
│   │   ├── registration_steps.py
│   │   ├── login_steps.py
│   │   └── shopping_steps.py
│   ├── environment.py         # Behave hooks and setup
│   ├── user_registration.feature
│   ├── user_login.feature
│   └── ecommerce_shopping.feature
├── pages/                     # Page Object Model
│   ├── base_page.py
│   ├── login_page.py
│   ├── registration_page.py
│   ├── products_page.py
│   ├── product_detail_page.py
│   └── cart_page.py
├── utils/                     # Utility classes
│   ├── database_utils.py
│   ├── api_client.py
│   └── email_utils.py
├── config/                    # Configuration files
│   └── config.py
├── data/                      # Test data
│   └── test_data/
├── reports/                   # Test reports
│   ├── screenshots/
│   └── junit/
├── logs/                      # Test execution logs
├── requirements.txt           # Python dependencies
├── behave.ini                # Behave configuration
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Chrome/Firefox/Edge browser
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd bdd-selenium-framework
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
nano .env  # or use your preferred editor
```

### 5. Database Setup (Optional)

If using database testing, set up your database and update the connection details in `.env`:

```bash
# PostgreSQL example
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test_db
DB_USER=test_user
DB_PASSWORD=test_password
DB_TYPE=postgresql
```

## 🎯 Quick Start

### Run All Tests

```bash
behave
```

### Run Specific Feature

```bash
behave features/user_login.feature
```

### Run Tests with Tags

```bash
# Run only smoke tests
behave --tags=@smoke

# Run specific scenarios
behave --tags=@registration

# Exclude work-in-progress tests
behave --tags="not @wip"
```

### Run with Different Browser

```bash
# Chrome (default)
behave

# Firefox
behave -D browser=firefox

# Edge
behave -D browser=edge

# Headless mode
behave -D headless=true
```

### Run with Different Environment

```bash
# Staging (default)
behave

# Development
behave -D environment=development

# Production
behave -D environment=production
```

## 📊 Reporting

### Allure Reports

```bash
# Generate Allure report
allure serve reports/allure

# Or generate static report
allure generate reports/allure --clean
allure open allure-report
```

### JUnit Reports

JUnit XML reports are automatically generated in `reports/junit/` directory.

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `BROWSER` | Browser choice (chrome/firefox/edge) | chrome |
| `HEADLESS` | Run in headless mode | false |
| `BASE_URL` | Application base URL | https://demo-ecommerce.com |
| `ENVIRONMENT` | Test environment | staging |
| `IMPLICIT_WAIT` | Implicit wait timeout | 10 |
| `TAKE_SCREENSHOTS_ON_FAILURE` | Screenshot on failure | true |

### Behave Configuration

Configure Behave behavior in `behave.ini`:

```ini
[behave]
default_format = pretty
color = true
show_skipped = false
format = pretty
        allure_behave.formatter:AllureFormatter
```

## 🧪 Writing Tests

### Feature Files

Create feature files in Gherkin syntax:

```gherkin
Feature: User Login
  As a registered user
  I want to login to my account
  So that I can access my dashboard

  @smoke @login
  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter login credentials:
      | email    | test@example.com |
      | password | SecurePass123!   |
    And I click login button
    Then I should be redirected to dashboard
```

### Step Definitions

Implement step definitions:

```python
from behave import given, when, then
from pages.login_page import LoginPage

@given('I am on the login page')
def step_navigate_to_login(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.navigate_to_login()

@when('I enter login credentials')
def step_enter_credentials(context):
    for row in context.table:
        if row['email']:
            context.login_page.enter_email(row['email'])
        if row['password']:
            context.login_page.enter_password(row['password'])
```

### Page Objects

Create page objects following the pattern:

```python
from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    # Locators
    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "loginButton")
    
    def enter_email(self, email):
        self.enter_text(self.EMAIL_INPUT, email)
    
    def enter_password(self, password):
        self.enter_text(self.PASSWORD_INPUT, password)
    
    def click_login_button(self):
        self.click_element(self.LOGIN_BUTTON)
```

## 🔄 CI/CD Integration

### GitHub Actions

Create `.github/workflows/tests.yml`:

```yaml
name: BDD Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        behave --tags=@smoke
      env:
        HEADLESS: true
        BROWSER: chrome
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Test') {
            steps {
                sh 'behave --tags=@smoke'
            }
        }
        
        stage('Report') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'index.html',
                    reportName: 'BDD Test Report'
                ])
            }
        }
    }
}
```

## 🏷️ Test Tags

Use tags to organize and run specific test groups:

- `@smoke` - Critical functionality tests
- `@regression` - Full regression suite
- `@api` - API-specific tests
- `@negative` - Negative test scenarios
- `@wip` - Work in progress (excluded by default)

Example usage:

```bash
# Run smoke tests only
behave --tags=@smoke

# Run everything except WIP
behave --tags="not @wip"

# Run smoke and regression
behave --tags="@smoke or @regression"
```

## 🛠️ Debugging

### Debug Mode

```bash
# Run with verbose output
behave --verbose

# Stop on first failure
behave --stop

# Run specific scenario
behave features/user_login.feature:10
```

### Screenshots

Screenshots are automatically taken on failures and saved in `reports/screenshots/`.

### Logs

Detailed logs are saved in `logs/test_execution.log`.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📝 Best Practices

### Test Design

- Write clear, descriptive Gherkin scenarios
- Use Page Object Model for better maintainability
- Keep step definitions simple and reusable
- Use tags to organize tests effectively

### Code Organization

- Follow Python naming conventions
- Add docstrings to all classes and methods
- Keep configuration separate from code
- Use meaningful variable and method names

### Test Data Management

- Use external data files for test data
- Implement data cleanup after tests
- Use faker library for generating test data
- Separate test data by environment

## ❓ FAQ

**Q: How do I run tests in parallel?**
A: Set `PARALLEL_PROCESSES` environment variable:
```bash
export PARALLEL_PROCESSES=4
behave --processes 4
```

**Q: How do I add a new browser?**
A: Extend the `initialize_driver` function in `features/environment.py` and add browser-specific setup.

**Q: How do I integrate with a test management tool?**
A: Use the JUnit XML output or extend the reporting to integrate with tools like TestRail or Zephyr.

**Q: How do I handle dynamic elements?**
A: Use explicit waits in the `BasePage` class methods like `wait_for_element_visible()`.

## 📞 Support

For issues and questions:
- Create GitHub issues
- Check existing documentation
- Review logs in `logs/` directory
- Enable debug mode for detailed output

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy Testing! 🎉**