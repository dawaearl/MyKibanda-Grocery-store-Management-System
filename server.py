from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge
from mysql.connector import pooling
import bcrypt
import os
from datetime import timedelta

from employees import register_employee
import products_dao
import orders_dao
import uom_dao

# Database connection pool config
dbconfig = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "narc2004",
    "database": "grocerystore",
    "pool_name": "mypool",
    "pool_size": 5
}

# Initialize connection pool
connection_pool = pooling.MySQLConnectionPool(**dbconfig)

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB limit
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300  # Cache static files for 5 minutes

def get_db_connection():
    return connection_pool.get_connection()

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/index')
def index():
    if 'employee_id' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('employee_login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
        
    if request.method == 'POST':
        # Get form data
        employee_data = {
            'employee_id': request.form['employee_id'],
            'employees_name': request.form['employees_name'],
            'password': request.form['password']
        }
        
        # Validate data
        if not all(employee_data.values()):
            return render_template('register.html', error='All fields are required')
            
        # Register employee
        success, message = register_employee(employee_data)
        
        if success:
            return redirect(url_for('employee_login'))
        else:
            return render_template('register.html', error=message)

@app.route('/new-order')
def newOrder():
    return render_template('order.html')

@app.route('/employee-login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            employee_id = request.form['employeeId']
            password = request.form['password']
            
            cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
            employee = cursor.fetchone()
            
            if employee and bcrypt.checkpw(password.encode('utf-8'), employee['password'].encode('utf-8')):
                session['employee_id'] = employee['employee_id']
                print("Login successful, redirecting to index")
                return redirect(url_for('index'))  # Ensure redirect on successful login
            
            print("Invalid credentials")
            return render_template('login.html', error='Invalid credentials')
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    return render_template('login.html')

@app.route('/manage-products')
def manageProducts():
    return render_template('manage-product.html')


@app.route('/getUOM', methods=['GET'])
def get_uom():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get UOMs and process response
        uoms = uom_dao.get_uoms(cursor)
        response = jsonify(uoms)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/getProducts', methods=['GET'])
def get_products():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get products in chunks
        products = products_dao.get_all_products(cursor)
        
        # Process in chunks of 100
        chunk_size = 100
        response = []
        for i in range(0, len(products), chunk_size):
            chunk = products[i:i + chunk_size]
            response.extend(chunk)
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/insertProduct', methods=['POST'])
def insert_product():
    connection = None
    cursor = None
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415
            
        request_payload = request.get_json()
        print(f"Received payload: {request_payload}")  # Debug log
        
        # Validate required fields and data types
        required_fields = {'name': str, 'uom_id': int, 'price_per_unit': (int, float)}
        for field, field_type in required_fields.items():
            if field not in request_payload:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            if not isinstance(request_payload[field], field_type):
                return jsonify({'error': f'Invalid type for field {field}. Expected {field_type}'}), 400
        
        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Verify UOM exists
            cursor.execute("SELECT uom_id FROM uom WHERE uom_id = %s", (request_payload['uom_id'],))
            if not cursor.fetchone():
                return jsonify({'error': f"UOM ID {request_payload['uom_id']} does not exist"}), 400
            
            # Insert product
            cursor.execute("""
                INSERT INTO products (name, uom_id, price_per_unit)
                VALUES (%s, %s, %s)
            """, (
                request_payload['name'],
                request_payload['uom_id'],
                request_payload['price_per_unit']
            ))
            
            connection.commit()
            product_id = cursor.lastrowid
            
            response = jsonify({
                'product_id': product_id,
                'message': 'Product inserted successfully'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
            
        except Exception as e:
            print(f"Database error: {str(e)}")  # Debug log
            connection.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
            
    except Exception as e:
        print(f"Server error: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/getAllOrders', methods=['GET'])
def get_all_orders():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get orders in chunks
        orders = orders_dao.get_all_orders(cursor)
        
        # Process in chunks of 50
        chunk_size = 50
        response = []
        for i in range(0, len(orders), chunk_size):
            chunk = orders[i:i + chunk_size]
            # Convert datetime objects to string
            for order in chunk:
                if 'datetime' in order:
                    order['datetime'] = order['datetime'].isoformat()
            response.extend(chunk)
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# In server.py
@app.route('/insertOrder', methods=['POST'])
def insert_order():
    connection = None
    cursor = None
    try:
        request_payload = request.get_json()
        print(f"Order payload received: {request_payload}")
        
        # Validate request payload
        if not request_payload.get('customer_name'):
            return jsonify({'error': 'Customer name is required'}), 400
            
        if not request_payload.get('grand_total'):
            return jsonify({'error': 'Grand total is required'}), 400
            
        if not request_payload.get('order_items'):
            return jsonify({'error': 'Order items are required'}), 400
            
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            order_id = orders_dao.insert_order(cursor, request_payload)
            connection.commit()
            
            response = jsonify({'order_id': order_id})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
            
        except Exception as e:
            print(f"Database error: {str(e)}")
            connection.rollback()
            return jsonify({'error': 'Error saving order. Please try again.'}), 500
            
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/deleteProduct', methods=['POST'])
def delete_product():
    connection = None
    cursor = None
    try:
        print("Received delete request")  # Debug log
        
        # Get product_id from request
        product_id = None
        if request.is_json:
            data = request.get_json()
            print(f"JSON data received: {data}")  # Debug log
            product_id = data.get('product_id')
        else:
            print(f"Form data received: {request.form}")  # Debug log
            product_id = request.form.get('product_id')
            
        # Validate product_id
        if not product_id:
            print("Missing product_id")  # Debug log
            return jsonify({'error': 'Missing product_id'}), 400
            
        # Convert product_id to integer
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid product_id format'}), 400
            
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if product exists
        cursor.execute("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
        if not cursor.fetchone():
            return jsonify({'error': f'Product with ID {product_id} not found'}), 404
            
        # Delete product
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        connection.commit()
        
        response = jsonify({
            'message': f'Product {product_id} deleted successfully'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        print(f"Error deleting product: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Session cleanup
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

# Static file handling with caching
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename, max_age=300)

if __name__ == "__main__":
    print("Starting Python Flask Server For Grocery Store Management System")
    app.run(port=5000, threaded=True, processes=1)