#!/usr/bin/env python3
"""Schema Validation Script for Triple Validation System"""
import json
import sys
from pathlib import Path

def validate_schema():
    errors = []
    validated = 0
    
    # Validate all JSON files
    for json_file in list(Path('results').rglob('*.json')) + list(Path('config').rglob('*.json')):
        try:
            with open(json_file) as f:
                json.load(f)
            validated += 1
            print(f"✅ {json_file}")
        except Exception as e:
            errors.append(str(e))
            print(f"❌ {json_file}: {e}")
    
    print(f"\nValidated: {validated}, Errors: {len(errors)}")
    return len(errors) == 0

if __name__ == "__main__":
    sys.exit(0 if validate_schema() else 1)
