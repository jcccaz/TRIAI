
import os

log_file = 'error.log'
if os.path.exists(log_file):
    try:
        with open(log_file, 'r', encoding='utf-16-le') as f:
            lines = f.readlines()
            print("".join(lines[-20:]))
    except Exception as e:
        print(f"Error reading utf-16-le: {e}")
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print("".join(lines[-20:]))
        except Exception as e2:
            print(f"Error reading utf-8: {e2}")
else:
    print("error.log not found")
