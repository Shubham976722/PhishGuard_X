
from getpass import getpass

from backend.app.database import SessionLocal
from backend.app.models.user import User
from backend.app.utils.security import hash_password


db = SessionLocal()

try:
    email = input("Enter registered email: ").strip().lower()

    user = db.query(User).filter(User.email == email).first()

    if not user:
        print("User not found.")
    else:
        password = getpass("Enter new password: ")
        confirm_password = getpass("Confirm new password: ")

        if password != confirm_password:
            print("Passwords do not match.")
        elif len(password) < 8:
            print("Password must contain at least 8 characters.")
        else:
            user.hashed_password = hash_password(password)
            db.commit()
            print("Password reset successfully.")

finally:
    db.close()
