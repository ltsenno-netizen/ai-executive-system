#!/usr/bin/env python3
import ast
import sys

def check_syntax(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        print(f"✓ {file_path}: Syntax OK")
        return True
    except SyntaxError as e:
        print(f"✗ {file_path}: Syntax Error - {e}")
        return False
    except Exception as e:
        print(f"✗ {file_path}: Error - {e}")
        return False

if __name__ == "__main__":
    files_to_check = [
        "src/backend/app/models/talent_management_extended.py",
        "src/backend/app/services/talent_management_engine.py",
        "src/backend/app/routes/talent_management_extended.py"
    ]

    all_ok = True
    for file_path in files_to_check:
        if not check_syntax(file_path):
            all_ok = False

    sys.exit(0 if all_ok else 1)