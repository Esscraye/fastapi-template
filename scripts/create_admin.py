import sys
import os
from sqlalchemy.orm import Session
from core.database import SessionLocal, Base, engine
from v1.models.user import User
from core.security import hash_password

# Chargement des variables d'environnement depuis .env si présent
from dotenv import load_dotenv
load_dotenv()

def create_admin(email: str, password: str):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"[INFO] Admin déjà existant: {email}")
        return
    admin = User(email=email, hashed_password=hash_password(password), is_active=True, role="admin")
    db.add(admin)
    db.commit()
    print(f"[OK] Admin créé: {email}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/create_admin.py <email> <password>")
        sys.exit(1)
    email = sys.argv[1]
    password = sys.argv[2]
    create_admin(email, password)

if __name__ == "__main__":
    main()
