import requests

BASE_URL = "http://localhost:8000"


def main() -> None:
    health = requests.get(f"{BASE_URL}/health", timeout=10)
    print("Health:", health.json())

    with open("sample_docs/company_policy.txt", "rb") as file:
        upload = requests.post(
            f"{BASE_URL}/documents",
            files={"file": ("company_policy.txt", file, "text/plain")},
            timeout=120,
        )
    print("Upload:", upload.status_code, upload.json())

    ask = requests.post(
        f"{BASE_URL}/ask",
        json={"question": "When should support escalate a ticket to engineering?", "top_k": 3},
        timeout=120,
    )
    print("Ask:", ask.status_code, ask.json())


if __name__ == "__main__":
    main()
