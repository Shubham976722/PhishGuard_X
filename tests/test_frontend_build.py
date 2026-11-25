import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def test_frontend_package_json():
    pkg_file = FRONTEND_DIR / "package.json"
    assert pkg_file.exists(), "frontend/package.json must exist"

    pkg = json.loads(pkg_file.read_text(encoding="utf-8"))
    assert "react" in pkg.get("dependencies", {})
    assert "react-dom" in pkg.get("dependencies", {})
    assert "vite" in pkg.get("devDependencies", {})
    assert "build" in pkg.get("scripts", {})


def test_frontend_production_build_artifacts():
    dist_dir = FRONTEND_DIR / "dist"
    assert dist_dir.exists(), "frontend/dist must exist after build"

    index_html = dist_dir / "index.html"
    assert index_html.exists(), "dist/index.html must exist"
    assert len(index_html.read_text(encoding="utf-8")) > 100

    assets_dir = dist_dir / "assets"
    assert assets_dir.exists(), "dist/assets must exist"

    js_files = list(assets_dir.glob("*.js"))
    css_files = list(assets_dir.glob("*.css"))

    assert len(js_files) >= 1, "At least one bundled JS artifact must exist"
    assert len(css_files) >= 1, "At least one bundled CSS artifact must exist"


def test_frontend_api_endpoints_coverage():
    api_file = FRONTEND_DIR / "src" / "services" / "api.js"
    assert api_file.exists()

    content = api_file.read_text(encoding="utf-8")

    # Verify coverage of all essential backend API contracts
    expected_endpoints = [
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/me",
        "/api/v1/scans/",
        "/api/v1/scans/history",
        "/api/v1/assistant/ask",
        "/api/v1/assistant/ask-scan/",
        "/api/v1/health/ready",
    ]

    for ep in expected_endpoints:
        assert ep in content, f"Frontend API client must implement endpoint {ep}"
