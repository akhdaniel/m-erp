import jwt
import json

# The new JWT token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJwZXJtaXNzaW9ucyI6WyJ2aWV3X2F1ZGl0X2xvZ3MiLCJpbnZlbnRvcnkuYWNjZXNzIiwiYWNjZXNzX2FkbWluX2Rhc2hib2FyZCIsInNldHRpbmdzLmFjY2VzcyIsIm1hbmFnZV9zeXN0ZW0iLCJxdW90ZXMudmlldyIsInNhbGVzLmFjY2VzcyIsInN0b2NrLnZpZXciLCJvcmRlcnMudmlldyIsIm1lbnUuY29uZmlndXJhdGlvbiIsIndhcmVob3VzZXMudmlldyIsIm1hbmFnZV9jdXJyZW5jaWVzIiwiY3VzdG9tZXJzLnZpZXciLCJtYW5hZ2Vfcm9sZXMiLCJwcm9kdWN0cy52aWV3IiwibWFuYWdlX2NvbXBhbmllcyIsInByb2R1Y3RzLm1hbmFnZSIsIm1hbmFnZV91c2VycyIsIm1hbmFnZV9wYXJ0bmVycyIsImludm9pY2VzLnZpZXciLCJyZWNlaXZpbmcudmlldyJdLCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2NjA5NjkwLjc0Mzg2MiwiZXhwIjoxNzU2NjEwNTkwLjc0Mzg2MiwibmJmIjoxNzU2NjA5NjkwLjc0Mzg2Mn0.cp049Ggyd9wTHfD0b4kWDumMnG1Aznt34qL3uIIcfu4"

# Try to decode without verification first to see the payload
try:
    payload = jwt.decode(token, options={"verify_signature": False})
    print("Payload without verification:")
    print(json.dumps(payload, indent=2))
except Exception as e:
    print(f"Error decoding without verification: {e}")

# Try to decode with verification using the secret key
secret_key = "development-secret-key-change-in-production"
try:
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    print("\nPayload with verification:")
    print(json.dumps(payload, indent=2))
except Exception as e:
    print(f"Error decoding with verification: {e}")