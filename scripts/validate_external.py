#!/usr/bin/env python3
"""External Verification Script"""
import os
import sys

def validate_external():
    verified = 0
    
    if os.environ.get('GEMINI_API_KEY'):
        print("✅ Gemini API Key present")
        verified += 1
    else:
        print("⚠️ Gemini API Key not set")
    
    if os.environ.get('GCP_SA_KEY'):
        print("✅ GCP SA Key present")
        verified += 1
    else:
        print("⚠️ GCP SA Key not set")
    
    return verified >= 1

if __name__ == "__main__":
    sys.exit(0 if validate_external() else 1)
