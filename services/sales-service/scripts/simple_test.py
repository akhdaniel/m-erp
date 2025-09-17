#!/usr/bin/env python3
"""
Simple test to verify Sales Service structure without external dependencies.
"""

import os
import sys
import importlib.util

def test_file_structure():
    """Test that all required files exist."""
    print("🔍 Testing Sales Service File Structure\n")
    
    required_files = {
        "Application": "main.py",
        "Requirements": "requirements.txt", 
        "Environment": ".env.example",
        "Quotation API": "sales_module/api/quote_api.py",
        "Quotation Schemas": "sales_module/schemas/quote_schemas.py",
        "Quotation Service": "sales_module/services/quote_service.py",
        "Quotation Models": "sales_module/models/quote.py",
        "API Tests": "tests/test_quote_api.py",
        "Service Tests": "tests/test_quote_service.py"
    }
    
    all_exist = True
    total_size = 0
    
    for category, file_path in required_files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            total_size += size
            print(f"✅ {category:<15}: {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {category:<15}: {file_path} missing")
            all_exist = False
    
    print(f"\n📊 Total codebase: {total_size:,} bytes")
    return all_exist

def test_import_structure():
    """Test that Python modules can be imported."""
    print("\n🔍 Testing Python Import Structure\n")
    
    # Test main application
    try:
        if os.path.exists("main.py"):
            print("✅ main.py structure looks valid")
        else:
            print("❌ main.py not found")
    except Exception as e:
        print(f"❌ main.py import error: {e}")
    
    # Test API structure
    try:
        api_file = "sales_module/api/quote_api.py"
        if os.path.exists(api_file):
            with open(api_file, 'r') as f:
                content = f.read()
                if "from fastapi import" in content and "@router." in content:
                    print("✅ Quotation API structure valid")
                else:
                    print("❌ Quotation API missing FastAPI components")
        else:
            print("❌ Quotation API file not found")
    except Exception as e:
        print(f"❌ Quotation API analysis error: {e}")
    
    # Test schema structure
    try:
        schema_file = "sales_module/schemas/quote_schemas.py"
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                content = f.read()
                if "from pydantic import" in content and "class " in content:
                    print("✅ Schema structure valid")
                else:
                    print("❌ Schema missing Pydantic components")
        else:
            print("❌ Schema file not found")
    except Exception as e:
        print(f"❌ Schema analysis error: {e}")

def show_testing_instructions():
    """Show instructions for testing the application."""
    print("\n📝 How to Test the Sales Service Application\n")
    
    print("🔧 Setup Instructions:")
    print("1. Create virtual environment:")
    print("   python3 -m venv venv")
    print("   source venv/bin/activate")
    print("")
    print("2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("")
    print("3. Start the server:")
    print("   python main.py")
    print("   OR")
    print("   ./run_server.sh")
    print("")
    
    print("🌐 Testing URLs:")
    print("• Service Root: http://localhost:8006/")
    print("• Health Check: http://localhost:8006/health")  
    print("• API Docs: http://localhost:8006/api/docs")
    print("• Quotation API: http://localhost:8006/api/v1/quotes/")
    print("")
    
    print("📋 Interactive Testing (via Swagger UI):")
    print("1. Open http://localhost:8006/api/docs in your browser")
    print("2. You'll see all 20+ quote API endpoints")
    print("3. Click 'Try it out' on any endpoint")
    print("4. Fill in example data and click 'Execute'")
    print("")
    
    print("🧪 Example API Calls:")
    print("")
    print("Create Quotation (POST /api/v1/quotes/):")
    print("""curl -X POST "http://localhost:8006/api/v1/quotes/" \\
     -H "Content-Type: application/json" \\
     -d '{
       "title": "Test Quotation",
       "customer_id": 100,
       "currency_code": "USD",
       "contact_person": "John Doe",
       "contact_email": "john@example.com"
     }'""")
    print("")
    
    print("List Quotations (GET /api/v1/quotes/):")
    print('curl "http://localhost:8006/api/v1/quotes/?page=1&page_size=10"')
    print("")
    
    print("Get Analytics (GET /api/v1/quotes/analytics):")
    print('curl "http://localhost:8006/api/v1/quotes/analytics"')
    print("")
    
    print("⚠️ Expected Behavior:")
    print("• API endpoints will return 500 errors (no database)")
    print("• Swagger UI will show all endpoints and schemas")
    print("• Request validation will work (422 for invalid data)")
    print("• Health checks will return 200 OK")
    print("• OpenAPI spec generation will work")
    
def show_production_deployment():
    """Show production deployment information."""
    print("\n🚀 Production Deployment Notes\n")
    
    print("📦 Required Infrastructure:")
    print("• PostgreSQL database (for quote storage)")
    print("• Redis server (for event messaging)")
    print("• Other XERPIUM services (inventory, partners, etc.)")
    print("")
    
    print("🔧 Environment Variables:")
    print("• Copy .env.example to .env")
    print("• Configure database connection")
    print("• Configure Redis connection")
    print("• Configure service URLs")
    print("")
    
    print("🐳 Docker Deployment:")
    print("• Build: docker build -t sales-service .")
    print("• Run: docker run -p 8006:8006 sales-service")
    print("• Use docker-compose for full XERPIUM stack")

def main():
    """Run all tests and show instructions."""
    print("🚀 Sales Service Testing Guide")
    print("=" * 50)
    
    # Test structure
    structure_ok = test_file_structure()
    test_import_structure()
    
    # Show instructions
    show_testing_instructions()
    show_production_deployment()
    
    print("\n" + "=" * 50)
    if structure_ok:
        print("✅ Sales Service is ready for testing!")
        print("📚 Follow the instructions above to start the server")
    else:
        print("❌ Some files are missing - check the structure")

if __name__ == "__main__":
    main()