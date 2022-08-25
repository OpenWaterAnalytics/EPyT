""" Delete all patterns from network file

  This example contains:
    Load network.
    Delete all patterns.
    Save new file without patterns.
    Unload library.
   
"""
from epyt import epanet


# Load network
d = epanet('Net1.inp')

# Delete all patterns
while d.getPatternIndex():
    indexPat = d.getPatternIndex()
    d.deletePattern(indexPat[0])

# Save new file without patterns
d.saveInputFile('No_patterns.inp')

# Unload library
d.unload()