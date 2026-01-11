#!/usr/bin/env python3
"""Cross-Reference Validation Script"""
import sys
from pathlib import Path

def validate_cross_reference():
    modules = [
        'src/core/manus_core.py',
        'src/pipeline/autonomous_pipeline.py',
        'src/validation/validation_system.py'
    ]
    
    passed = 0
    for module in modules:
        if Path(module).exists():
            try:
                with open(module) as f:
                    compile(f.read(), module, 'exec')
                passed += 1
                print(f"✅ {module}")
            except SyntaxError:
                print(f"❌ {module}: Syntax error")
        else:
            print(f"❌ {module}: Missing")
    
    return passed == len(modules)

if __name__ == "__main__":
    sys.exit(0 if validate_cross_reference() else 1)
