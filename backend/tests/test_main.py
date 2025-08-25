from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# check /health endpoint
def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

# check /version has expected keys
def test_version_has_keys():
    r = client.get("/version")
    assert r.status_code == 200
    body = r.json()
    assert "version" in body
    assert "host_ip" in body

# check /version respects env variable
def test_version_env_override(monkeypatch):
    monkeypatch.setenv("BACKEND_VERSION", "1.2.3-test")
    r = client.get("/version")
    assert r.status_code == 200
    assert r.json()["version"] == "1.2.3-test"

# check OpenAPI schema contains paths
def test_openapi_contains_paths():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    data = r.json()
    for path in ["/health", "/version"]:
        assert path in data["paths"]

# check non-existing route returns 404
def test_unknown_route_404():
    r = client.get("/no-such-route")
    assert r.status_code == 404
    assert r.json().get("detail") in ("Not Found", "Not Found.")

# check CORS headers for simple GET
def test_cors_headers_on_get():
    r = client.get("/health", headers={"Origin": "http://example.com"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "*"

# check CORS headers for preflight OPTIONS
def test_cors_preflight_options():
    origin = "http://example.com"
    r = client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code in (200, 204)
    allow_origin = r.headers.get("access-control-allow-origin")
    assert allow_origin in ("*", origin)
    assert r.headers.get("access-control-allow-credentials") in ("true", "True")
    allow_methods = r.headers.get("access-control-allow-methods")
    assert allow_methods is None or "GET" in allow_methods or allow_methods == "*"
