#!/usr/bin/env python3
"""
Test syntax error auto-fix
"""

print("Testing syntax error fix")

# Intentional syntax error - missing colon
if True:
    print("This should be fixed")

print("End of test")