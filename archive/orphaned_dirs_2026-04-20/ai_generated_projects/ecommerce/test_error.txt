#!/usr/bin/env python3
"""
Test Error File - To Test Debug Button
"""

import nonexistent_module_that_will_never_exist
import another_missing_module

def broken_function():
    # This will cause a runtime error
    undefined_variable_that_will_cause_error.some_method()
    missing_class = UndefinedClass()
    return missing_class.call_nonexistent_method()

if __name__ == "__main__":
    broken_function()
    print("This should fail with import error")