from datetime import datetime
from sql_connection import get_sql_connection

def insert_order(cursor, order):
    try:
        # Insert main order
        order_query = ("INSERT INTO orders "
                      "(customer_name, total, datetime) "
                      "VALUES (%s, %s, %s)")
        order_data = (order['customer_name'], order['grand_total'], datetime.now())
        
        cursor.execute(order_query, order_data)
        order_id = cursor.lastrowid
        
        # Insert order items
        if order['order_items']:
            order_details_query = ("INSERT INTO order_details "
                                 "(order_id, product_id, quantity, total) "
                                 "VALUES (%s, %s, %s, %s)")
            
            order_details_data = [
                (order_id, item['product_id'], item['quantity'], item['total_price'])
                for item in order['order_items']
            ]
            
            cursor.executemany(order_details_query, order_details_data)
        
        return order_id
        
    except Exception as e:
        print(f"Database error in insert_order: {str(e)}")
        raise

def get_order_details(connection, order_id):
    cursor = connection.cursor()

    query = "SELECT * from order_details where order_id = %s"

    query = "SELECT order_details.order_id, order_details.quantity, order_details.total, "\
            "products.name, products.price_per_unit FROM order_details LEFT JOIN products on " \
            "order_details.product_id = products.product_id where order_details.order_id = %s"

    data = (order_id, )

    cursor.execute(query, data)

    records = []
    for (order_id, quantity, total, product_name, price_per_unit) in cursor:
        records.append({
            'order_id': order_id,
            'quantity': quantity,
            'total': total,
            'product_name': product_name,
            'price_per_unit': price_per_unit
        })

    cursor.close()

    return records

def get_all_orders(cursor):
    try:
        cursor.execute("""
            SELECT o.order_id, 
                   o.customer_name, 
                   o.total, 
                   o.datetime
            FROM orders o
            ORDER BY o.datetime DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return []

if __name__ == '__main__':
    connection = get_sql_connection()
    print(get_all_orders(connection.cursor()))