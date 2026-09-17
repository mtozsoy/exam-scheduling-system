import urllib.request
import json
import urllib.error
import urllib.parse
from uuid import uuid4

BASE_URL = "http://127.0.0.1:8000"

def login(username, password):
    data = urllib.parse.urlencode({'username': username, 'password': password}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/v1/auth/login", data=data)
    try:
        with urllib.request.urlopen(req) as response:
            return response.getcode(), json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def make_request(method, endpoint, token=None, json_data=None):
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    
    data = None
    if json_data is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(json_data).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}{endpoint}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read()
            return response.getcode(), json.loads(content.decode()) if content else None
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def run_tests():
    print("Running Auth & Roles tests...")
    
    # 1. Doğru login
    status, data = login("admin", "admin123")
    assert status == 200, f"Expected 200, got {status}"
    admin_token = data["access_token"]
    print("[PASS] Doğru login -> 200 + token")

    # 2. Yanlış şifre
    status, _ = login("admin", "wrong_password")
    assert status == 401, f"Expected 401, got {status}"
    print("[PASS] Yanlış şifre -> 401")

    # 3. Token olmadan protected endpoint
    status, _ = make_request("GET", "/api/v1/courses")
    assert status == 401, f"Expected 401, got {status}"
    print("[PASS] Token olmadan protected endpoint -> 401")

    # 4. Admin kullanıcı yönetimine erişebiliyor
    status, users = make_request("GET", "/api/v1/users", token=admin_token)
    assert status == 200, f"Expected 200, got {status}"
    print("[PASS] Admin kullanıcı yönetimine erişebiliyor -> 200")

    # 5. Kullanıcı oluşturma (Secretary)
    test_sec_username = f"sec_{uuid4().hex[:6]}"
    status, new_user = make_request("POST", "/api/v1/users", token=admin_token, json_data={
        "KullaniciAdi": test_sec_username,
        "password": "secpassword",
        "Rol": "secretary"
    })
    assert status == 200, f"Expected 200, got {status}"
    sec_id = new_user["KullaniciID"]
    print(f"[PASS] Kullanıcı oluşturma başarılı (ID: {sec_id})")

    # 6. Secretary login & yetki kontrolleri
    status, sec_data = login(test_sec_username, "secpassword")
    assert status == 200
    sec_token = sec_data["access_token"]

    status, _ = make_request("GET", "/api/v1/courses", token=sec_token)
    assert status == 200, f"Expected 200, got {status}"
    print("[PASS] Secretary -> kendi yetkilerine erişebiliyor (GET /courses) -> 200")

    status, _ = make_request("GET", "/api/v1/users", token=sec_token)
    assert status == 403, f"Expected 403, got {status}"
    print("[PASS] Secretary -> Admin-only endpoint'e erişemiyor (GET /users) -> 403")

    # 7. Rol değiştirme (Admin yetkisiyle)
    status, updated_user = make_request("PUT", f"/api/v1/users/{sec_id}", token=admin_token, json_data={
        "Rol": "admin"
    })
    assert status == 200 and updated_user["Rol"] == "admin"
    print("[PASS] Rol değiştirme başarılı")

    # 8. Kendi kendini silme engeli (Admin kendi hesabını silmeyi dener)
    admin_id = next(u["KullaniciID"] for u in users if u["KullaniciAdi"] == "admin")
    status, err = make_request("DELETE", f"/api/v1/users/{admin_id}", token=admin_token)
    assert status == 400 and "Cannot delete your own account" in err["detail"]
    print("[PASS] Kendi kendini silme engellendi -> 400")

    # 9. Kullanıcı silme (Oluşturduğumuz test kullanıcısını silelim - Cleanup)
    status, _ = make_request("DELETE", f"/api/v1/users/{sec_id}", token=admin_token)
    assert status == 204, f"Expected 204, got {status}"
    print("[PASS] Kullanıcı silme başarılı (Cleanup tamamlandı) -> 204")

    print("\nTüm testler başarıyla geçti!")

if __name__ == "__main__":
    run_tests()
