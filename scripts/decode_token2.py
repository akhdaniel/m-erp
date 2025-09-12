import jwt
import json

# The JWT token from the curl request
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJwZXJtaXNzaW9ucyI6WyJ2aWV3X2F1ZGl0X2xvZ3MiLCJpbnZlbnRvcnkuYWNjZXNzIiwiYWNjZXNzX2FkbWluX2Rhc2hib2FyZCIsInNldHRpbmdzLmFjY2VzcyIsIm1hbmFnZV9zeXN0ZW0iLCJxdW90ZXMudmlldyIsInNhbGVzLmFjY2VzcyIsInN0b2NrLnZpZXciLCJvcmRlcnMudmlldyIsIm1lbnUuYWNjZXNzIiwid2FyZWhvdXNlcy52aWV3IiwibWFuYWdlX2N1cnJlbmNpZXMiLCJjdXN0b21lcnMudmlldyIsIm1hbmFnZV9yb2xlcyIsInByb2R1Y3RzLnZpZXciLCJtYW5hZ2VfY29tcGFuaWVzIiwicHJvZHVjdHMubWFuYWdlIiwibWFuYWdlX3VzZXJzIiwibWFuYWdlX3BhcnRuZXJzIiwiaW52b2ljZXMudmlldyIsInJlY2VpdmluZy52aWV3Il0sInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjE3NTY2MDgzODguNTM3ODAzLCJleHAiOjE3NTY2MDkyODguNTM3ODAzLCJuYmYiOjE3NTY2MDgzODguNTM3ODAzfQ.mmYy1tgRksEtFva-qhPvObWJb3xtU5Okyjj-g4heEU0"

# Try to decode with HS256 algorithm
secret_key = "development-secret-key-change-in-production"
try:
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    print("Payload with HS256 verification:")
    print(json.dumps(payload, indent=2))
except Exception as e:
    print(f"Error decoding with HS256: {e}")

# Try to decode with HS512 algorithm
try:
    payload = jwt.decode(token, secret_key, algorithms=["HS512"])
    print("\nPayload with HS512 verification:")
    print(json.dumps(payload, indent=2))
except Exception as e:
    print(f"Error decoding with HS512: {e}")

# Try to decode with RS256 algorithm
try:
    payload = jwt.decode(token, secret_key, algorithms=["RS256"])
    print("\nPayload with RS256 verification:")
    print(json.dumps(payload, indent=2))
except Exception as e:
    print(f"Error decoding with RS256: {e}")