import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def seed_admin():
    db = SessionLocal()
    try:
        admin_username = os.environ.get("DEFAULT_ADMIN_USER", "admin")
        admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin123")
        
        existing = db.query(User).filter(User.KullaniciAdi == admin_username).first()
        if existing:
            print(f"Admin user '{admin_username}' already exists.")
            return

        admin_user = User(
            KullaniciAdi=admin_username,
            SifreHash=get_password_hash(admin_password),
            Rol="admin"
        )
        db.add(admin_user)
        db.commit()
        print(f"Admin user '{admin_username}' created successfully.")
    except Exception as e:
        print(f"Error seeding admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
