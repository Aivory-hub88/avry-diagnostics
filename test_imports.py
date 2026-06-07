#!/usr/bin/env python
"""Import validation test - Generic for all services"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    service_name = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
    print("=" * 60)
    print(f"IMPORT TESTS - {service_name.upper()}")
    print("=" * 60)
    
    modules_to_test = [
        "main",
        "app.config",
        "app.database.db_service",
        "app.routes.diagnostic",
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"[OK] {module:<40} PASS")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {module:<40} ERROR")
            print(f"  {str(e)[:60]}")
            errors.append((module, str(e)))
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
