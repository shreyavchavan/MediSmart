import requests
import json

def test_interaction():
    url = "http://localhost:8000/api/check-interactions"
    data = {
        "medicines": ["Aspirin", "Warfarin"]
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_interaction()
