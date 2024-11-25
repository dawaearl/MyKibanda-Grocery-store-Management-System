import unittest
import sys
import os
import json
import bcrypt

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server import app, get_db_connection

class TestFlaskApi(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Insert test data
        self.connection = get_db_connection()
        self.cursor = self.connection.cursor(dictionary=True)
        
        # Insert test employee
        self.employee_id = '1'
        self.password = 'test123'
        hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.cursor.execute("""
            INSERT INTO employees (employee_id, employees_name, password)
            VALUES (%s, %s, %s)
        """, (self.employee_id, 'Test Employee', hashed_password))
        
        self.connection.commit()

    def tearDown(self):
        # Clean up test data
        self.cursor.execute("DELETE FROM employees WHERE employee_id = %s", (self.employee_id,))
        self.connection.commit()
        
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def test_employee_login(self):
        # Test login with valid credentials
        response = self.app.post('/employee-login', data={
            'employeeId': self.employee_id,
            'password': self.password
        })
        print(response.data)  # Debug log
        self.assertEqual(response.status_code, 302)  # Expecting 302 for successful login
    
    def test_get_products(self):
        response = self.app.get('/getProducts')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

if __name__ == '__main__':
    unittest.main()