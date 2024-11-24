from flask import Flask, request, jsonify, render_template
from sql_connection import get_sql_connection
import json
from werkzeug.exceptions import RequestEntityTooLarge

import products_dao
import orders_dao
import uom_dao

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

connection = get_sql_connection()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new-order')
def newOrder():
    return render_template('order.html')

@app.route('/manage-products')
def manageProducts():
    return render_template('manage-product.html')


@app.route('/getUOM', methods=['GET'])
def get_uom():
    response = uom_dao.get_uoms(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/getProducts', methods=['GET'])
def get_products():
    response = products_dao.get_all_products(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/insertProduct', methods=['POST'])
def insert_product():
    try:
        request_payload = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'uom_id', 'price_per_unit']
        for field in required_fields:
            if field not in request_payload or not request_payload[field]:
                return jsonify({'error': f'Missing or empty {field}'}), 400
        
        # Validate uom_id is a valid integer
        try:
            request_payload['uom_id'] = int(request_payload['uom_id'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid uom_id value'}), 400
            
        product_id = products_dao.insert_new_product(connection, request_payload)
        response = jsonify({'product_id': product_id})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/getAllOrders', methods=['GET'])
def get_all_orders():
    orders = orders_dao.get_all_orders(connection)
    for order in orders:
        order['datetime'] = order['datetime'].isoformat()  # Ensure datetime is in ISO 8601 format
    response = jsonify(orders)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# In server.py
@app.route('/insertOrder', methods=['POST'])
def insert_order():
    try:
        request_payload = request.get_json()
        print("Order payload received:", request_payload)
        
        # Validate required fields
        if not request_payload.get('customer_name'):
            return jsonify({'error': 'Customer name is required'}), 400
            
        if not request_payload.get('grand_total'):
            return jsonify({'error': 'Grand total is required'}), 400
            
        if not request_payload.get('order_items'):
            return jsonify({'error': 'Order items are required'}), 400
            
        if not isinstance(request_payload['order_items'], list) or len(request_payload['order_items']) == 0:
            return jsonify({'error': 'Order must contain at least one item'}), 400

        order_id = orders_dao.insert_order(connection, request_payload)
        response = jsonify({'order_id': order_id})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        print(f"Error processing order: {str(e)}")
        return jsonify({'error': str(e)}), 500



@app.route('/deleteProduct', methods=['POST'])
def delete_product():
    try:
        if request.is_json:
            data = request.get_json()
            product_id = data.get('product_id')
        else:
            product_id = request.form.get('product_id')
            
        if not product_id:
            return jsonify({'error': 'Missing product_id'}), 400
            
        return_id = products_dao.delete_product(connection, product_id)
        response = jsonify({
            'product_id': return_id
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except RequestEntityTooLarge:
        return jsonify({'error': 'Request too large'}), 413
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("Starting Python Flask Server For Grocery Store Management System")
    app.run(port=5000)