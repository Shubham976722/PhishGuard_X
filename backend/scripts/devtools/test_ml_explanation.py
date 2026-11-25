
from backend.app.services.ml_service import (
    predict_url,
    explain_url
)

url = "http://secure-login-verify-account.example.com/login"

prediction = predict_url(url)
explanation = explain_url(url)

print("\nPREDICTION")
print(prediction)

print("\nTOP CONTRIBUTING FEATURES")

for item in explanation["top_factors"]:
    direction = (
        "Increases phishing risk"
        if item["contribution"] > 0
        else "Decreases phishing risk"
    )

    print(
        f"{item['feature']}: "
        f"value={item['value']}, "
        f"contribution={item['contribution']}, "
        f"{direction}"
    )
