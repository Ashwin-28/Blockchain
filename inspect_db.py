import sqlite3
import os
import json

DB_PATH = 'backend/biometric_identity.db'

def inspect_db():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("📊 Tables:")
        for t in tables:
            print(f"- {t[0]}")
        print("\n")

        # Get Subjects
        print(f"👥 Subjects:")
        cursor.execute("SELECT id, name, biometric_type, created_at FROM subjects")
        subjects = cursor.fetchall()
        if not subjects:
            print("   (No subjects found)")
        for s in subjects:
            print(f"   ID: {s[0]} | Name: {s[1]} | Type: {s[2]} | Created: {s[3]}")

        # Get Logs
        print(f"\n📝 Recent Auth Logs:")
        cursor.execute("SELECT subject_id, success, failure_reason, created_at FROM authentication_logs ORDER BY created_at DESC LIMIT 5")
        logs = cursor.fetchall()
        if not logs:
             print("   (No logs found)")
        for l in logs:
            status = "✅ Success" if l[1] else "❌ Failed"
            print(f"   {status} | Subject: {l[0][:8]}... | Reason: {l[2]} | Time: {l[3]}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_db()
