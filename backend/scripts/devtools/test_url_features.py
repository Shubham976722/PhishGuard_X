
from backend.app.services.url_features import extract_url_features


test_urls = [
    "https://example.com",
    "http://192.168.1.1/login",
    "https://example.com/verify-account",
]

for url in test_urls:
    print("\nURL:", url)
    print(extract_url_features(url))
