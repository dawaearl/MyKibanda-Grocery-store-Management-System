from sql_connection import get_sql_connection

def get_all_products(cursor):
    try:
        cursor.execute("""
            SELECT products.product_id, products.name, products.uom_id, products.price_per_unit, uom.uom_name 
            FROM products INNER JOIN uom ON products.uom_id = uom.uom_id
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

def insert_new_product(connection, product):
    cursor = connection.cursor()
    query = ("INSERT INTO products "
             "(name, uom_id, price_per_unit)"
             "VALUES (%s, %s, %s)")
    data = (product['name'], int(product['uom_id']), product['price_per_unit'])
    cursor.execute(query, data)
    connection.commit()

    return cursor.lastrowid


def delete_product(connection, product_id):
    cursor = connection.cursor()
    query = ("DELETE FROM products where product_id=" +str(product_id))
    cursor.execute(query)
    connection.commit()

    return cursor.lastrowid




if __name__ =='__main__':
    connection = get_sql_connection()
    #print(delete_product(connection, 4))
    print(insert_new_product(connection, {
        'name': 'potatoes',
        'uom_id': 1,
        'price_per_unit': 10
    }))





  #""""""
 # {
  #     'product_name': 'cabbage',
  #      'uom_id': '1',
  #      'price_per_unit': '10'
   # }