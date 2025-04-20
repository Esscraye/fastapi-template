import uuid

def test_create_user(client, user_data):
    response = client.post("/v1/users/", json=user_data)
    assert response.status_code == 201, f"Response: {response.status_code}, Body: {response.text}"
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "created_at" in data

def test_create_user_duplicate(client, user_data):
    client.post("/v1/users/", json=user_data)
    response = client.post("/v1/users/", json=user_data)
    assert response.status_code == 400, f"Response: {response.status_code}, Body: {response.text}"
    assert response.json()["detail"] == "Email already registered"

def test_get_user(client, user_data, user_token):
    # user_data déjà créé par user_token
    response = client.get("/v1/users/1", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200, f"Response: {response.status_code}, Body: {response.text}"
    data = response.json()
    assert data["email"] == user_data["email"]

def test_get_user_not_found(client, user_token):
    response = client.get("/v1/users/9999", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 404, f"Response: {response.status_code}, Body: {response.text}"
    assert response.json()["detail"] == "User not found"

def test_list_users(client, admin_token):
    # Seul un admin peut lister les users
    resp = client.get("/v1/users/?skip=0&limit=5", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200, f"Response: {resp.status_code}, Body: {resp.text}"
    users = resp.json()
    assert isinstance(users, list)
    assert len(users) >= 1

def test_update_user(client, user_data, admin_token):
    # user_data déjà créé par user_token
    update_data = {"email": "updated@example.com", "password": "newpassword", "is_active": False}
    response = client.put("/v1/users/1", json=update_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200, f"Response: {response.status_code}, Body: {response.text}"
    data = response.json()
    assert data["email"] == update_data["email"]
    assert data["is_active"] is False

def test_partial_update_user(client, user_data, admin_token):
    patch_data = {"is_active": False}
    response = client.patch("/v1/users/1", json=patch_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200, f"Response: {response.status_code}, Body: {response.text}"
    data = response.json()
    assert data["is_active"] is False

def test_delete_user(client, user_data, admin_token):
    response = client.delete("/v1/users/1", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 204, f"Response: {response.status_code}, Body: {response.text}"
    get_resp = client.get("/v1/users/1", headers={"Authorization": f"Bearer {admin_token}"})
    # Après suppression, certains backends renvoient 401 (Unauthorized) si le token n'est plus valide, d'autres 404 (Not found)
    assert get_resp.status_code in (401, 404)

def test_login_token(client, user_data):
    client.post("/v1/users/", json=user_data)
    response = client.post("/v1/users/token", data={"username": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 200, f"Response: {response.status_code}, Body: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_token_fail(client, user_data):
    response = client.post("/v1/users/token", data={"username": user_data["email"], "password": "wrong"})
    assert response.status_code == 401, f"Response: {response.status_code}, Body: {response.text}"

def test_get_user_auth(client, user_data, get_token):
    client.post("/v1/users/", json=user_data)
    # Récupère l'utilisateur créé
    token = get_token
    resp = client.get("/v1/users/1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, f"Response: {resp.status_code}, Body: {resp.text}"

def test_get_user_unauth(client, user_data):
    client.post("/v1/users/", json=user_data)
    resp = client.get("/v1/users/1")
    assert resp.status_code == 401, f"Response: {resp.status_code}, Body: {resp.text}"

def test_list_users_auth(client, admin_token):
    resp = client.get("/v1/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200, f"Response: {resp.status_code}, Body: {resp.text}"
    assert isinstance(resp.json(), list)

def test_list_users_unauth(client):
    resp = client.get("/v1/users/")
    assert resp.status_code == 401, f"Response: {resp.status_code}, Body: {resp.text}"

def test_admin_can_list_users(client, admin_token):
    resp = client.get("/v1/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200, f"Response: {resp.status_code}, Body: {resp.text}"
    assert isinstance(resp.json(), list)

def test_user_cannot_list_users(client, user_token):
    resp = client.get("/v1/users/", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403, f"Response: {resp.status_code}, Body: {resp.text}"

def test_user_cannot_create_admin(client, user_token):
    # Crée d'abord un admin pour activer la restriction
    admin_data = {"email": f"admin_{uuid.uuid4().hex[:8]}@example.com", "password": "adminpass", "role": "admin"}
    resp_admin = client.post("/v1/users/", json=admin_data)
    assert resp_admin.status_code == 201, f"Admin bootstrap failed: {resp_admin.status_code}, {resp_admin.text}"

    # Un user standard tente de créer un admin (doit échouer)
    resp = client.post("/v1/users/", json={"email": "newadmin@example.com", "password": "adminpass", "role": "admin"}, headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403, f"Response: {resp.status_code}, Body: {resp.text}"

def test_admin_can_create_admin(client, admin_token):
    resp = client.post("/v1/users/", json={"email": "secondadmin@example.com", "password": "adminpass", "role": "admin"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201, f"Response: {resp.status_code}, Body: {resp.text}"
    assert resp.json()["role"] == "admin"

def test_user_cannot_update_other_user(client, user_token):
    # Crée un autre utilisateur avec un email unique
    another_user = {"email": f"user_{uuid.uuid4().hex[:8]}@example.com", "password": "anotherpassword", "role": "user"}
    client.post("/v1/users/", json=another_user)
    # User tente de faire un PUT sur un autre user
    resp = client.put("/v1/users/2", json={"email": "hacked@example.com"}, headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403, f"Response: {resp.status_code}, Body: {resp.text}"

def test_admin_can_update_user(client, admin_token, user_data):
    # Crée un user
    client.post("/v1/users/", json=user_data)
    # Admin met à jour le user
    resp = client.put("/v1/users/1", json={"email": "updated@example.com"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200, f"Response: {resp.status_code}, Body: {resp.text}"
    assert resp.json()["email"] == "updated@example.com"

def test_user_cannot_delete_user(client, user_token):
    another_user = {"email": f"user_{uuid.uuid4().hex[:8]}@example.com", "password": "anotherpassword", "role": "user"}
    client.post("/v1/users/", json=another_user)
    resp = client.delete("/v1/users/2", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403, f"Response: {resp.status_code}, Body: {resp.text}"

def test_admin_can_delete_user(client, admin_token, user_data):
    client.post("/v1/users/", json=user_data)
    resp = client.delete("/v1/users/1", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 204, f"Response: {resp.status_code}, Body: {resp.text}"
