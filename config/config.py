import os
from configparser import ConfigParser
from dotenv import load_dotenv

class Config:
    """Main configuration class for the BDD framework"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize config parser
        self.config_parser = ConfigParser()
        
        # Define config file path
        self.config_file = os.path.join(os.path.dirname(__file__), 'test_config.ini')
        
        # Load config file if it exists
        if os.path.exists(self.config_file):
            self.config_parser.read(self.config_file)
        
        # Initialize configuration
        self._initialize_config()
    
    def _initialize_config(self):
        """Initialize all configuration values"""
        
        # Browser Configuration
        self.BROWSER = os.getenv('BROWSER', 'chrome').lower()
        self.HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
        self.BROWSER_WIDTH = int(os.getenv('BROWSER_WIDTH', '1920'))
        self.BROWSER_HEIGHT = int(os.getenv('BROWSER_HEIGHT', '1080'))
        
        # Application URLs
        self.BASE_URL = os.getenv('BASE_URL', 'https://demo-ecommerce.com')
        self.API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.demo-ecommerce.com')
        
        # Test Environment
        self.ENVIRONMENT = os.getenv('ENVIRONMENT', 'staging').lower()
        
        # Timeouts
        self.IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))
        self.EXPLICIT_WAIT = int(os.getenv('EXPLICIT_WAIT', '10'))
        self.PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
        
        # Database Configuration
        self.DB_HOST = os.getenv('DB_HOST', 'localhost')
        self.DB_PORT = int(os.getenv('DB_PORT', '5432'))
        self.DB_NAME = os.getenv('DB_NAME', 'test_db')
        self.DB_USER = os.getenv('DB_USER', 'test_user')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'test_password')
        self.DB_TYPE = os.getenv('DB_TYPE', 'postgresql')  # postgresql, mysql, sqlite
        
        # Email Configuration (for email testing)
        self.EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
        self.EMAIL_USER = os.getenv('EMAIL_USER', '')
        self.EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
        self.EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
        
        # Test Data
        self.TEST_DATA_DIR = os.getenv('TEST_DATA_DIR', 'data/test_data')
        
        # Reporting
        self.REPORT_DIR = os.getenv('REPORT_DIR', 'reports')
        self.SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR', 'reports/screenshots')
        self.LOG_DIR = os.getenv('LOG_DIR', 'logs')
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        # Parallel Execution
        self.PARALLEL_PROCESSES = int(os.getenv('PARALLEL_PROCESSES', '1'))
        
        # API Configuration
        self.API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
        self.API_RETRIES = int(os.getenv('API_RETRIES', '3'))
        
        # Browser Options
        self.CHROME_OPTIONS = self._get_chrome_options()
        self.FIREFOX_OPTIONS = self._get_firefox_options()
        
        # Test User Credentials
        self.TEST_USERS = {
            'valid_user': {
                'email': os.getenv('TEST_USER_EMAIL', 'test@example.com'),
                'password': os.getenv('TEST_USER_PASSWORD', 'SecurePass123!')
            },
            'admin_user': {
                'email': os.getenv('ADMIN_USER_EMAIL', 'admin@example.com'),
                'password': os.getenv('ADMIN_USER_PASSWORD', 'AdminPass123!')
            }
        }
        
        # Feature Flags
        self.ENABLE_API_TESTING = os.getenv('ENABLE_API_TESTING', 'true').lower() == 'true'
        self.ENABLE_DATABASE_TESTING = os.getenv('ENABLE_DATABASE_TESTING', 'true').lower() == 'true'
        self.ENABLE_EMAIL_TESTING = os.getenv('ENABLE_EMAIL_TESTING', 'false').lower() == 'true'
        self.TAKE_SCREENSHOTS_ON_FAILURE = os.getenv('TAKE_SCREENSHOTS_ON_FAILURE', 'true').lower() == 'true'
        
        # Load environment-specific configs
        self._load_environment_config()
    
    def _get_chrome_options(self):
        """Get Chrome browser options"""
        options = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--ignore-certificate-errors',
            '--ignore-ssl-errors',
            '--ignore-certificate-errors-spki-list',
            '--ignore-certificate-errors-ssl',
            f'--window-size={self.BROWSER_WIDTH},{self.BROWSER_HEIGHT}'
        ]
        
        if self.HEADLESS:
            options.append('--headless')
        
        return options
    
    def _get_firefox_options(self):
        """Get Firefox browser options"""
        options = []
        
        if self.HEADLESS:
            options.append('--headless')
        
        return options
    
    def _load_environment_config(self):
        """Load environment-specific configuration"""
        env_configs = {
            'development': {
                'BASE_URL': 'http://localhost:3000',
                'API_BASE_URL': 'http://localhost:8000/api',
                'DB_HOST': 'localhost'
            },
            'staging': {
                'BASE_URL': 'https://staging.demo-ecommerce.com',
                'API_BASE_URL': 'https://api-staging.demo-ecommerce.com',
                'DB_HOST': 'staging-db.demo-ecommerce.com'
            },
            'production': {
                'BASE_URL': 'https://demo-ecommerce.com',
                'API_BASE_URL': 'https://api.demo-ecommerce.com',
                'DB_HOST': 'prod-db.demo-ecommerce.com'
            }
        }
        
        if self.ENVIRONMENT in env_configs:
            env_config = env_configs[self.ENVIRONMENT]
            for key, value in env_config.items():
                # Only override if not set via environment variable
                if not os.getenv(key):
                    setattr(self, key, value)
    
    def get_database_url(self):
        """Get database connection URL"""
        if self.DB_TYPE == 'postgresql':
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        elif self.DB_TYPE == 'mysql':
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        elif self.DB_TYPE == 'sqlite':
            return f"sqlite:///{self.DB_NAME}.db"
        else:
            raise ValueError(f"Unsupported database type: {self.DB_TYPE}")
    
    def get_test_user(self, user_type='valid_user'):
        """Get test user credentials"""
        return self.TEST_USERS.get(user_type, self.TEST_USERS['valid_user'])
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.REPORT_DIR,
            self.SCREENSHOT_DIR,
            self.LOG_DIR,
            self.TEST_DATA_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def update_config(self, **kwargs):
        """Update configuration values dynamically"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Configuration key '{key}' does not exist")
    
    def get_config_dict(self):
        """Get all configuration as dictionary"""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }