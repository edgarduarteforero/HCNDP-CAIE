# -*- coding: utf-8 -*-
"""
Created on Tue May  7 10:32:33 2024

@author: edgar
"""

from modulefinder import ModuleFinder
f = ModuleFinder()

# Run the main script
f.run_script('local_search.py')

# Get names of all the imported modules
names = list(f.modules.keys())

# Get a sorted list of the root modules imported
basemods = sorted(set([name.split('.')[0] for name in names]))
# Print it nicely
print("\n".join(basemods))