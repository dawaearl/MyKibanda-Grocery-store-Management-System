from sql_connection import get_sql_connection
import bcrypt

connection = get_sql_connection()

def hash_existing_passwords():
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT employee_id, password FROM employees")
    employees = cursor.fetchall()
    
    for employee in employees:
        # Check if the password is already hashed
        try:
            bcrypt.checkpw('test'.encode('utf-8'), employee['password'].encode('utf-8'))
        except ValueError:
            # If not hashed, hash the password
            hashed_password = bcrypt.hashpw(employee['password'].encode('utf-8'), bcrypt.gensalt())
            cursor.execute("UPDATE employees SET password = %s WHERE employee_id = %s", (hashed_password.decode('utf-8'), employee['employee_id']))
    
    connection.commit()
    cursor.close()

if __name__ == "__main__":
    hash_existing_passwords()