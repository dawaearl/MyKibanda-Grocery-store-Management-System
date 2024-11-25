from datetime import datetime

def get_uoms(cursor):
    try:
        cursor.execute("SELECT * FROM uom")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching UOMs: {e}")
        return []


def insert_order(connection, order):
    try:
        cursor = connection.cursor()
        
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
                                 "(order_id, product_id, quantity, total_price) "
                                 "VALUES (%s, %s, %s, %s)")
            
            order_details_data = [
                (order_id, item['product_id'], item['quantity'], item['total_price'])
                for item in order['order_items']
            ]
            
            cursor.executemany(order_details_query, order_details_data)
        
        connection.commit()
        return order_id
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        connection.rollback()
        raise


def insert_product(cursor, product_data):
    try:
        cursor.execute("""
            INSERT INTO products (name, uom_id, price_per_unit)
            VALUES (%s, %s, %s)
        """, (
            product_data['name'],
            product_data['uom_id'],
            product_data['price_per_unit']
        ))
        return cursor.lastrowid
    except Exception as e:
        print(f"Error in insert_product: {e}")
        raise


if __name__ == '__main__':
    from sql_connection import get_sql_connection

    connection = get_sql_connection()
    cursor = connection.cursor()
    print(get_uoms(cursor))