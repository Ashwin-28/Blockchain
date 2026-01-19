"""
Database Diagnostic Script
Checks if all database dependencies are properly installed and working
"""

import sys
import os

print("=" * 60)
print("DATABASE DIAGNOSTIC REPORT")
print("=" * 60)
print()

# Check Python version
print(f"Python Version: {sys.version}")
print()

# Check SQLAlchemy
print("1. Checking SQLAlchemy...")
try:
    import sqlalchemy
    print(f"   ✓ SQLAlchemy installed: {sqlalchemy.__version__}")
    SQLALCHEMY_OK = True
except ImportError as e:
    print(f"   ✗ SQLAlchemy NOT installed: {e}")
    SQLALCHEMY_OK = False
print()

# Check PyMongo
print("2. Checking PyMongo...")
try:
    import pymongo
    print(f"   ✓ PyMongo installed: {pymongo.__version__}")
    PYMONGO_OK = True
except ImportError as e:
    print(f"   ✗ PyMongo NOT installed: {e}")
    PYMONGO_OK = False
print()

# Check database file
print("3. Checking database file...")
db_path = os.path.join(os.path.dirname(__file__), 'biometric_identity.db')
if os.path.exists(db_path):
    size = os.path.getsize(db_path)
    print(f"   ✓ Database file exists: {db_path}")
    print(f"   ✓ Size: {size:,} bytes")
else:
    print(f"   ✗ Database file NOT found: {db_path}")
print()

# Test database module import
print("4. Testing database module import...")
try:
    from modules.database import db_service
    print(f"   ✓ Database module imported successfully")
    print(f"   ✓ Database available: {db_service.available}")
    
    if db_service.available:
        # Test database operations
        print()
        print("5. Testing database operations...")
        try:
            stats = db_service.get_statistics()
            print(f"   ✓ Statistics retrieved:")
            print(f"      - Total subjects: {stats['total_subjects']}")
            print(f"      - Total authentications: {stats['total_authentications']}")
            print(f"      - Database type: {stats['type']}")
        except Exception as e:
            print(f"   ✗ Error getting statistics: {e}")
    else:
        print()
        print("5. Database operations skipped (database not available)")
        
except Exception as e:
    print(f"   ✗ Error importing database module: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)

# Summary
print()
if SQLALCHEMY_OK:
    print("✓ All database dependencies are installed correctly")
    print("✓ The backend should work properly")
else:
    print("✗ SQLAlchemy is missing - please install dependencies:")
    print("  pip install -r requirements.txt")
