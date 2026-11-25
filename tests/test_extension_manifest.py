import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_DIR = PROJECT_ROOT / "browser-extension"
MANIFEST_PATH = EXTENSION_DIR / "manifest.json"


def test_manifest_file_exists():
    assert MANIFEST_PATH.exists(), "manifest.json must exist in browser-extension/"


def test_manifest_v3_structure():
    content = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert content.get("manifest_version") == 3, "Extension must use Manifest V3"
    assert content.get("name") == "PhishGuard X - AI Phishing Protection"
    assert content.get("version") == "1.0.0"

    # Background service worker check
    background = content.get("background", {})
    assert "service_worker" in background, "Must declare service_worker"
    worker_path = EXTENSION_DIR / background["service_worker"]
    assert worker_path.exists(), f"Service worker file {worker_path} must exist"

    # Action popup check
    action = content.get("action", {})
    assert "default_popup" in action, "Must declare default_popup"
    popup_path = EXTENSION_DIR / action["default_popup"]
    assert popup_path.exists(), f"Popup file {popup_path} must exist"


def test_manifest_least_privilege_permissions():
    content = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    permissions = content.get("permissions", [])

    # Ensure least privilege: no broad <all_urls>, no webRequestBlocking, no cookies
    assert "activeTab" in permissions, "Must request activeTab for current-tab scanning"
    assert "storage" in permissions, "Must request storage for auth token cache"

    forbidden_permissions = ["<all_urls>", "webRequestBlocking", "cookies", "history", "management"]
    for forbidden in forbidden_permissions:
        assert forbidden not in permissions, f"Permission {forbidden} violates least privilege"


def test_manifest_icons_exist_and_valid_png():
    content = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    icons = content.get("icons", {})

    assert set(icons.keys()) == {"16", "48", "128"}

    for size, icon_rel in icons.items():
        icon_path = EXTENSION_DIR / icon_rel
        assert icon_path.exists(), f"Icon {size} at {icon_path} must exist"
        data = icon_path.read_bytes()
        # Verify PNG magic header: \x89PNG\r\n\x1a\n
        assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"Icon {size} must be a valid PNG"


def test_extension_files_have_no_secrets():
    # Security check: ensure no API keys or database URLs leaked into extension code
    forbidden_tokens = ["postgres:", "JWT_SECRET", "URLHAUS_AUTH_KEY"]

    for ext_file in EXTENSION_DIR.rglob("*"):
        if ext_file.is_file() and ext_file.suffix in [".js", ".html", ".json", ".css"]:
            text = ext_file.read_text(encoding="utf-8", errors="ignore")
            for token in forbidden_tokens:
                assert token not in text, f"Secret token {token} found in {ext_file.name}"


def test_popup_assets_exist():
    popup_html = EXTENSION_DIR / "popup" / "popup.html"
    popup_css = EXTENSION_DIR / "popup" / "popup.css"
    popup_js = EXTENSION_DIR / "popup" / "popup.js"

    assert popup_html.exists()
    assert popup_css.exists()
    assert popup_js.exists()

    html_text = popup_html.read_text(encoding="utf-8")
    assert "popup.css" in html_text
    assert "popup.js" in html_text
