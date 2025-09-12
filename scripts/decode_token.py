import jwt
import json

# The JWT token from the curl request
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJwZXJtaXNzaW9ucyI6WyJ2aWV3X2F1ZGl0X2xvZ3MiLCJpbnZlbnRvcnkuYWNjZXNzIiwiYWNjZXNzX2FkbWluX2Rhc2hib2FyZCIsInNldHRpbmdzLmFjY2VzcyIsIm1hbmFnZV9zeXN0ZW0iLCJxdW90ZXMudmlldyIsInNhbGVzLmFjY2VzcyIsInN0b2NrLnZpZXciLCJvcmRlcnMudmlldyIsIm1lbnUuYWNjZXNzIiwid2FyZWhvdXNlcy52aWV3IiwibWFuYWdlX2N1cnJlbmNpZXMiLCJjdXN0b21lcnMudmlldyIsIm1hbmFnZV9yb2xlcyIsInByb2R1Y3RzLnZpZXciLCJtYW5hZ2VfY29tcGFuaWVzIiwicHJvZHVjdHMubWFuYWdlIiwibWFuYWdlX3VzZXJzIiwibWFuYWdlX3BhcnRuZXJzIiwiaW52b2ljZXMudmlldyIsInJlY2VpdmluZy52aWV3Il0sInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjE3NTY2MDgzODguNTM3ODAzLCJleHAiOjE3NTY2MDkyODguNTM3ODAzLCJuYmYiOjE3NTY2MDgzODguNTM3ODAzfQ.mmYy1tgRksEtFva-qhPvObWJb3xtU5Okyjj-g4heEU0"

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