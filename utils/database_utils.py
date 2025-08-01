import logging
import psycopg2
import mysql.connector
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config.config import Config
import hashlib
from datetime import datetime

class DatabaseManager:
    """Database utility class for test data management"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.engine = None
        self.session = None
        
    def connect(self):
        """Establish database connection"""
        try:
            if self.config.DB_TYPE == 'postgresql':
                self._connect_postgresql()
            elif self.config.DB_TYPE == 'mysql':
                self._connect_mysql()
            elif self.config.DB_TYPE == 'sqlite':
                self._connect_sqlite()
            else:
                raise ValueError(f"Unsupported database type: {self.config.DB_TYPE}")
                
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    def _connect_postgresql(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD
            )
            
            # SQLAlchemy engine
            self.engine = create_engine(self.config.get_database_url())
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            self.logger.info("Connected to PostgreSQL database")
            
        except Exception as e:
            self.logger.error(f"PostgreSQL connection failed: {e}")
            raise
    
    def _connect_mysql(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD
            )
            
            # SQLAlchemy engine
            self.engine = create_engine(self.config.get_database_url())
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            self.logger.info("Connected to MySQL database")
            
        except Exception as e:
            self.logger.error(f"MySQL connection failed: {e}")
            raise
    
    def _connect_sqlite(self):
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(f"{self.config.DB_NAME}.db")
            
            # SQLAlchemy engine
            self.engine = create_engine(self.config.get_database_url())
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            self.logger.info("Connected to SQLite database")
            
        except Exception as e:
            self.logger.error(f"SQLite connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        try:
            if self.session:
                self.session.close()
            if self.connection:
                self.connection.close()
            self.logger.info("Database connection closed")
        except Exception as e:
            self.logger.error(f"Error closing database connection: {e}")
    
    def execute_query(self, query, params=None):
        """Execute a SQL query"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in results]
            else:
                self.connection.commit()
                return cursor.rowcount
                
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_sqlalchemy_query(self, query, params=None):
        """Execute query using SQLAlchemy"""
        try:
            if not self.session:
                self.connect()
            
            if params:
                result = self.session.execute(text(query), params)
            else:
                result = self.session.execute(text(query))
            
            if query.strip().upper().startswith('SELECT'):
                return [dict(row) for row in result]
            else:
                self.session.commit()
                return result.rowcount
                
        except Exception as e:
            self.logger.error(f"SQLAlchemy query execution failed: {e}")
            if self.session:
                self.session.rollback()
            raise
    
    # User management methods
    def create_user(self, user_data):
        """Create a new user"""
        try:
            # Hash password
            password_hash = self._hash_password(user_data['password'])
            
            query = """
            INSERT INTO users (first_name, last_name, email, password_hash, phone, created_at, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            params = (
                user_data['first_name'],
                user_data['last_name'],
                user_data['email'],
                password_hash,
                user_data.get('phone', ''),
                datetime.now(),
                'active'
            )
            
            result = self.execute_query(query, params)
            user_id = result[0]['id'] if result else None
            
            self.logger.info(f"User created with ID: {user_id}")
            return user_id
            
        except Exception as e:
            self.logger.error(f"Failed to create user: {e}")
            raise
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            query = "SELECT * FROM users WHERE email = %s"
            result = self.execute_query(query, (email,))
            return result[0] if result else None
            
        except Exception as e:
            self.logger.error(f"Failed to get user by email: {e}")
            raise
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            query = "SELECT * FROM users WHERE id = %s"
            result = self.execute_query(query, (user_id,))
            return result[0] if result else None
            
        except Exception as e:
            self.logger.error(f"Failed to get user by ID: {e}")
            raise
    
    def update_user(self, user_id, user_data):
        """Update user information"""
        try:
            set_clauses = []
            params = []
            
            for field, value in user_data.items():
                if field == 'password':
                    set_clauses.append("password_hash = %s")
                    params.append(self._hash_password(value))
                else:
                    set_clauses.append(f"{field} = %s")
                    params.append(value)
            
            params.append(user_id)
            
            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s"
            
            rows_affected = self.execute_query(query, params)
            self.logger.info(f"Updated {rows_affected} user record(s)")
            
            return rows_affected
            
        except Exception as e:
            self.logger.error(f"Failed to update user: {e}")
            raise
    
    def delete_user(self, user_id):
        """Delete user by ID"""
        try:
            query = "DELETE FROM users WHERE id = %s"
            rows_affected = self.execute_query(query, (user_id,))
            self.logger.info(f"Deleted {rows_affected} user record(s)")
            return rows_affected
            
        except Exception as e:
            self.logger.error(f"Failed to delete user: {e}")
            raise
    
    # Product management methods
    def create_product(self, product_data):
        """Create a new product"""
        try:
            query = """
            INSERT INTO products (name, description, price, stock_quantity, category, brand, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            params = (
                product_data['name'],
                product_data['description'],
                product_data['price'],
                product_data['stock_quantity'],
                product_data['category'],
                product_data['brand'],
                datetime.now()
            )
            
            result = self.execute_query(query, params)
            product_id = result[0]['id'] if result else None
            
            self.logger.info(f"Product created with ID: {product_id}")
            return product_id
            
        except Exception as e:
            self.logger.error(f"Failed to create product: {e}")
            raise
    
    def get_product_by_name(self, name):
        """Get product by name"""
        try:
            query = "SELECT * FROM products WHERE name = %s"
            result = self.execute_query(query, (name,))
            return result[0] if result else None
            
        except Exception as e:
            self.logger.error(f"Failed to get product by name: {e}")
            raise
    
    def update_product_stock(self, product_name, stock_quantity):
        """Update product stock quantity"""
        try:
            query = "UPDATE products SET stock_quantity = %s WHERE name = %s"
            rows_affected = self.execute_query(query, (stock_quantity, product_name))
            self.logger.info(f"Updated stock for {product_name} to {stock_quantity}")
            return rows_affected
            
        except Exception as e:
            self.logger.error(f"Failed to update product stock: {e}")
            raise
    
    # Order management methods
    def create_order(self, order_data):
        """Create a new order"""
        try:
            query = """
            INSERT INTO orders (order_id, user_id, status, payment_status, total_amount, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            params = (
                order_data['order_id'],
                order_data['user_id'],
                order_data['status'],
                order_data['payment_status'],
                order_data['total_amount'],
                datetime.now()
            )
            
            result = self.execute_query(query, params)
            order_id = result[0]['id'] if result else None
            
            self.logger.info(f"Order created with ID: {order_id}")
            return order_id
            
        except Exception as e:
            self.logger.error(f"Failed to create order: {e}")
            raise
    
    def get_order_by_id(self, order_id):
        """Get order by ID"""
        try:
            query = "SELECT * FROM orders WHERE order_id = %s"
            result = self.execute_query(query, (order_id,))
            return result[0] if result else None
            
        except Exception as e:
            self.logger.error(f"Failed to get order by ID: {e}")
            raise
    
    def _hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def cleanup_test_data(self, test_run_id=None):
        """Clean up test data"""
        try:
            # Delete test orders
            self.execute_query("DELETE FROM orders WHERE created_at > NOW() - INTERVAL '1 day'")
            
            # Delete test users (excluding system users)
            self.execute_query("DELETE FROM users WHERE email LIKE '%test%' OR email LIKE '%example%'")
            
            # Reset product stock for test products
            self.execute_query("UPDATE products SET stock_quantity = 100 WHERE name LIKE '%test%'")
            
            self.logger.info("Test data cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup test data: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()