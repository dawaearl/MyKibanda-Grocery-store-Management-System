from datetime import datetime

def get_uoms(connection):
    cursor = connection.cursor()
    query = ("SELECT * FROM grocerystore.uom")
    cursor.execute(query)

    response = []
    for (uom_id, uom_name) in cursor:
        response.append ({
            'uom_id': uom_id,
            'uom_name': uom_name
        })
    return response


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


if __name__ == '__main__':
    from sql_connection import get_sql_connection

    connection = get_sql_connection()
    print(get_uoms(connection))