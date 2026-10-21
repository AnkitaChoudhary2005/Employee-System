
from src.utlis.db import LocalSession
from src.user.models import UserModel
from src.user.controller import hash_password

db = LocalSession()

try:
    email = "admin@example.com"
    password = "Admin@12345"

    existing_user = (
        db.query(UserModel)
        .filter(UserModel.email == email)
        .first()
    )

    if existing_user:
        print("This email already exists.")
        print("Email:", existing_user.email)
        print("Role:", existing_user.role)
    else:
        admin = UserModel(
            name="Admin",
            email=email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()
        print("Admin account created successfully!")
        print("Email:", email)
        print("Password:", password)

except Exception as e:
    db.rollback()
    print("Error creating admin:", e)

finally:
    db.close()
