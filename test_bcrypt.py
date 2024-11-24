# test_bcrypt.py
import bcrypt

def test_bcrypt():
    # Test password
    password = "test123"
    
    # Generate hash
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed}")
    
    # Verify hash
    is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed)
    print(f"Password verification: {is_valid}")

if __name__ == "__main__":
    test_bcrypt()