# Create Layers (Parcels in city that have impervious centroid within, Address points in city limits, all imperviousp,
# and temporary city layer to create these layers.)

# Select by attributes to filter out child parcels from stacked parcels

# Search cursor on Parcels [@SHAPE, ParcelID]:
# Loop through, select by location Impervious centroid inside and AP inside
# Of NO AP, ERROR: No AP, Check PARCEL ID, iterate

# Second Search Cursor Address Point Search Cursor [ID]
# Third Search Cursor for Impervious [ParcelID, APID]
#
# Two Loops NOT NESTED
# First loop to find correct AP Referenced for Impervious (Loop through AP)
# The correct AP will be the one it lands on, and carried to the next loop
# Should we check to make sure it hasn't reached End Of List?

# If AP/ID == Impervious/APID then:
#   break
#
# Second Loop to ensure correctness (Loop Through Impervious)
# if AP/ID != ImperviousID:
#   ERRPR: Parcel Contains incorrect AP : IMP assignmentgn

def main():
    pass

def
if __name__ == "__main__":
    main()
