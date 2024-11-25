import unittest
from mysql.connector import pooling
import bcrypt
from datetime import datetime

# Import your database configuration
dbconfig = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "narc2004",
    "database": "grocerystore",
    "pool_name": "mypool",
    "pool_size": 5
}

class TestDatabaseOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection_pool = pooling.MySQLConnectionPool(**dbconfig)

    def setUp(self):
        self.connection = self.connection_pool.get_connection()
        self.cursor = self.connection.cursor(dictionary=True)

    def tearDown(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def test_database_connection(self):
        self.assertTrue(self.connection.is_connected())

    def test_product_operations(self):
        # Test product insertion
        product_data = {
            'name': 'Test Product',
            'uom_id': 1,
            'price_per_unit': 10.99
        }
        
        self.cursor.execute("""
            INSERT INTO products (name, uom_id, price_per_unit)
            VALUES (%(name)s, %(uom_id)s, %(price_per_unit)s)
        """, product_data)
        
        product_id = self.cursor.lastrowid
        self.assertIsNotNone(product_id)

        # Test product retrieval
        self.cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = self.cursor.fetchone()
        self.assertEqual(product['name'], product_data['name'])

        # Clean up
        self.cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        self.connection.commit()

    def test_order_operations(self):
        # Test order insertion
        order_data = {
            'customer_name': 'Test Customer',
            'total': 100.00,
            'datetime': datetime.now()
        }
        
        self.cursor.execute("""
            INSERT INTO orders (customer_name, total, datetime)
            VALUES (%(customer_name)s, %(total)s, %(datetime)s)
        """, order_data)
        
        order_id = self.cursor.lastrowid
        self.assertIsNotNone(order_id)

        # Test order retrieval
        self.cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        order = self.cursor.fetchone()
        self.assertEqual(order['customer_name'], order_data['customer_name'])

        # Clean up
        self.cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        self.connection.commit()

    def test_employee_operations(self):
        # Test employee insertion
        employee_id = 123  # Specify a unique employee_id
        password = "test123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        employee_data = {
            'employee_id': employee_id,
            'employees_name': 'Test Employee',
            'password': hashed_password.decode('utf-8')
        }
        
        self.cursor.execute("""
            INSERT INTO employees (employee_id, employees_name, password)
            VALUES (%(employee_id)s, %(employees_name)s, %(password)s)
        """, employee_data)
        
        # Test employee retrieval
        self.cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
        employee = self.cursor.fetchone()
        self.assertEqual(employee['employees_name'], employee_data['employees_name'])

        # Test password verification
        self.assertTrue(
            bcrypt.checkpw(
                password.encode('utf-8'),
                employee['password'].encode('utf-8')
            )
        )

        # Clean up
        self.cursor.execute("DELETE FROM employees WHERE employee_id = %s", (employee_id,))
        self.connection.commit()

if __name__ == '__main__':
    unittest.main()