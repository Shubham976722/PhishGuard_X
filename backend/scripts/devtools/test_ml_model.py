
from backend.app.services.ml_service import predict_url
from backend.app.services.url_features import extract_url_features

urls = [
    "https://www.google.com",
    "https://www.google.com/"
]

for url in urls:
    print("\nURL:", url)

    print("FEATURES:")
    print(extract_url_features(url))

    print("\nPREDICTION:")
    print(predict_url(url))
