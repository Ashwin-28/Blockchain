import sys
import os

# Redirect stdout and stderr to a file internally
log_file = open('startup_debug.log', 'w', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

try:
    print("Starting app...")
    from app import app
    print("App imported successfully")
    # Try to run it for a few seconds and then exit
    # This is just to see if it imports and starts without crashing
    app.run(port=5001, debug=False) 
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
finally:
    log_file.close()
