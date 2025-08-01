import requests
import logging
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.config import Config
import time

class APIClient:
    """API client for REST API testing"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        self.base_url = self.config.API_BASE_URL
        self.session = self._create_session()
        self.default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _create_session(self):
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=self.config.API_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with logging and error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Set default timeout
        kwargs.setdefault('timeout', self.config.API_TIMEOUT)
        
        # Set default headers
        headers = kwargs.get('headers', {})
        headers.update(self.default_headers)
        kwargs['headers'] = headers
        
        self.logger.info(f"Making {method.upper()} request to: {url}")
        if 'json' in kwargs:
            self.logger.info(f"Request payload: {json.dumps(kwargs['json'], indent=2)}")
        
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, **kwargs)
            response_time = time.time() - start_time
            
            self.logger.info(f"Response Status: {response.status_code}")
            self.logger.info(f"Response Time: {response_time:.2f}s")
            
            # Log response for debugging
            try:
                response_json = response.json()
                self.logger.info(f"Response Body: {json.dumps(response_json, indent=2)}")
            except:
                self.logger.info(f"Response Body: {response.text}")
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response.json() if self._is_json_response(response) else response.text,
                'response_time': response_time,
                'raw_response': response
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return {
                'status_code': 0,
                'error': str(e),
                'response_time': time.time() - start_time
            }
    
    def _is_json_response(self, response):
        """Check if response is JSON"""
        content_type = response.headers.get('Content-Type', '')
        return 'application/json' in content_type
    
    def get(self, endpoint, **kwargs):
        """Make GET request"""
        return self._make_request('GET', endpoint, **kwargs)
    
    def post(self, endpoint, **kwargs):
        """Make POST request"""
        return self._make_request('POST', endpoint, **kwargs)
    
    def put(self, endpoint, **kwargs):
        """Make PUT request"""
        return self._make_request('PUT', endpoint, **kwargs)
    
    def patch(self, endpoint, **kwargs):
        """Make PATCH request"""
        return self._make_request('PATCH', endpoint, **kwargs)
    
    def delete(self, endpoint, **kwargs):
        """Make DELETE request"""
        return self._make_request('DELETE', endpoint, **kwargs)
    
    def set_auth_token(self, token):
        """Set authentication token"""
        self.default_headers['Authorization'] = f'Bearer {token}'
        self.logger.info("Authentication token set")
    
    def clear_auth_token(self):
        """Clear authentication token"""
        if 'Authorization' in self.default_headers:
            del self.default_headers['Authorization']
            self.logger.info("Authentication token cleared")
    
    # User-related API methods
    def register_user(self, user_data):
        """Register a new user"""
        return self.post('/auth/register', json=user_data)
    
    def login_user(self, email, password):
        """Login user"""
        login_data = {
            'email': email,
            'password': password
        }
        return self.post('/auth/login', json=login_data)
    
    def get_user_profile(self, user_id):
        """Get user profile"""
        return self.get(f'/users/{user_id}')
    
    def update_user_profile(self, user_id, user_data):
        """Update user profile"""
        return self.put(f'/users/{user_id}', json=user_data)
    
    # Product-related API methods
    def get_products(self, **filters):
        """Get products with optional filters"""
        return self.get('/products', params=filters)
    
    def get_product_by_id(self, product_id):
        """Get product by ID"""
        return self.get(f'/products/{product_id}')
    
    def search_products(self, query):
        """Search products"""
        return self.get('/products/search', params={'q': query})
    
    def create_product(self, product_data):
        """Create a new product (admin only)"""
        return self.post('/products', json=product_data)
    
    def update_product(self, product_id, product_data):
        """Update product (admin only)"""
        return self.put(f'/products/{product_id}', json=product_data)
    
    def delete_product(self, product_id):
        """Delete product (admin only)"""
        return self.delete(f'/products/{product_id}')
    
    # Cart-related API methods
    def get_cart(self, user_id):
        """Get user's cart"""
        return self.get(f'/users/{user_id}/cart')
    
    def add_to_cart(self, user_id, product_id, quantity=1):
        """Add item to cart"""
        cart_data = {
            'product_id': product_id,
            'quantity': quantity
        }
        return self.post(f'/users/{user_id}/cart', json=cart_data)
    
    def update_cart_item(self, user_id, item_id, quantity):
        """Update cart item quantity"""
        return self.put(f'/users/{user_id}/cart/{item_id}', json={'quantity': quantity})
    
    def remove_from_cart(self, user_id, item_id):
        """Remove item from cart"""
        return self.delete(f'/users/{user_id}/cart/{item_id}')
    
    def clear_cart(self, user_id):
        """Clear entire cart"""
        return self.delete(f'/users/{user_id}/cart')
    
    # Order-related API methods
    def create_order(self, order_data):
        """Create a new order"""
        return self.post('/orders', json=order_data)
    
    def get_order_details(self, order_id):
        """Get order details"""
        return self.get(f'/orders/{order_id}')
    
    def get_user_orders(self, user_id):
        """Get user's orders"""
        return self.get(f'/users/{user_id}/orders')
    
    def update_order_status(self, order_id, status):
        """Update order status (admin only)"""
        return self.patch(f'/orders/{order_id}', json={'status': status})
    
    def cancel_order(self, order_id):
        """Cancel order"""
        return self.patch(f'/orders/{order_id}/cancel')
    
    # Payment-related API methods
    def process_payment(self, payment_data):
        """Process payment"""
        return self.post('/payments', json=payment_data)
    
    def get_payment_status(self, payment_id):
        """Get payment status"""
        return self.get(f'/payments/{payment_id}')
    
    def refund_payment(self, payment_id, amount=None):
        """Refund payment"""
        refund_data = {}
        if amount:
            refund_data['amount'] = amount
        return self.post(f'/payments/{payment_id}/refund', json=refund_data)
    
    # Admin API methods
    def get_admin_stats(self):
        """Get admin dashboard statistics"""
        return self.get('/admin/stats')
    
    def get_all_users(self, page=1, limit=50):
        """Get all users (admin only)"""
        return self.get('/admin/users', params={'page': page, 'limit': limit})
    
    def get_all_orders(self, page=1, limit=50):
        """Get all orders (admin only)"""
        return self.get('/admin/orders', params={'page': page, 'limit': limit})
    
    # Utility methods
    def purchase_product(self, purchase_data):
        """Complete product purchase (for testing concurrent purchases)"""
        return self.post('/products/purchase', json=purchase_data)
    
    def health_check(self):
        """Check API health"""
        return self.get('/health')
    
    def verify_response_schema(self, response, expected_schema):
        """Verify response matches expected schema"""
        # This could use jsonschema library for validation
        # For now, basic validation
        if response['status_code'] != 200:
            return False
        
        data = response['data']
        for key in expected_schema:
            if key not in data:
                self.logger.error(f"Missing key in response: {key}")
                return False
        
        return True
    
    def wait_for_api_ready(self, max_attempts=30, delay=1):
        """Wait for API to be ready"""
        for attempt in range(max_attempts):
            try:
                response = self.health_check()
                if response['status_code'] == 200:
                    self.logger.info("API is ready")
                    return True
            except:
                pass
            
            self.logger.info(f"API not ready, attempt {attempt + 1}/{max_attempts}")
            time.sleep(delay)
        
        self.logger.error("API failed to become ready")
        return False