import os
os.environ["ENV_FILE"] = ".env.test"

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.environ["ENV_FILE"], override=True)
os.environ["DATABASE_URL"] = "sqlite:///file::memory:?cache=shared"

import pytest
from core.db_base import Base
from core.database import get_db, engine, SessionLocal
from main import app
from fastapi.testclient import TestClient
import uuid
# Ensure all models are imported so their tables are created

print(f"[TEST DEBUG] Using engine: {engine}")

# Ensure tables are created for the in-memory DB before tests
@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    Base.metadata.create_all(bind=engine)
    yield
    # Optionally: Base.metadata.drop_all(bind=engine)

# Ajout de fixtures pour générer des emails uniques et des données utilisateur, admin, etc.
@pytest.fixture
def unique_email():
    return f"user_{uuid.uuid4().hex[:8]}@example.com"

@pytest.fixture
def user_data(unique_email):
    return {"email": unique_email, "password": "strongpassword", "role": "user"}

@pytest.fixture
def another_user_data(unique_email):
    return {"email": unique_email, "password": "anotherpassword", "role": "user"}

@pytest.fixture
def admin_data(unique_email):
    return {"email": unique_email, "password": "adminpassword", "role": "admin"}

@pytest.fixture
def get_token(client, user_data):
    client.post("/v1/users/", json=user_data)
    response = client.post("/v1/users/token", data={"username": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def admin_token(client):
    email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
    admin_data = {"email": email, "password": "adminpassword", "role": "admin"}
    resp = client.post("/v1/users/", json=admin_data)
    assert resp.status_code == 201
    token_resp = client.post("/v1/users/token", data={"username": email, "password": "adminpassword"})
    assert token_resp.status_code == 200
    return token_resp.json()["access_token"]

@pytest.fixture
def user_token(client, user_data):
    client.post("/v1/users/", json=user_data)
    resp = client.post("/v1/users/token", data={"username": user_data["email"], "password": user_data["password"]})
    assert resp.status_code == 200
    return resp.json()["access_token"]

@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    print(f"[TEST DEBUG] Creating/dropping tables on engine: {engine}")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

# --- Suppression automatique du fichier file::memory: à la fin des tests ---
@pytest.fixture(scope="session", autouse=True)
def cleanup_memory_file():
    yield
    memfile = "file::memory:"
    if os.path.exists(memfile):
        try:
            os.remove(memfile)
            print(f"[TEST CLEANUP] Fichier supprimé : {memfile}")
        except Exception as e:
            print(f"[TEST CLEANUP] Erreur suppression {memfile} : {e}")
