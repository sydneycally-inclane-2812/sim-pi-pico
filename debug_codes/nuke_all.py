# Reset sys.path to its initial state (only the default paths)
import sys
sys.path = sys.path[:1]  # Retain only the base path

# Reset all imported modules
import os
import gc  # Garbage collector to clean up

# Clear loaded modules (except built-ins)
for module in list(sys.modules.keys()):
    if module not in ('sys', 'builtins', 'os', 'gc'):
        del sys.modules[module]

# Clear global variables (except built-ins and essential ones)
globals().clear()

# Manually re-import necessary modules
import os
import sys
import gc
gc.collect()  # Force garbage collection to clean up memory
