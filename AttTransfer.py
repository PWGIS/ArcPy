import arcpy

arcpy.env.workspace = "D:/Test.gdb"
arcpy.env.overwriteOutput = True
#
roadfeatures = "D:/Test.gdb/roadsSubset"
patchfeatures = "D:/Test.gdb/patch"
joinFeatures = r"D:\Test.gdb\roadsSubset"
targetFeatures = r"D:\Test.gdb\patch"
outputFeatures = r"D:\Test.gdb\PatchSJPoly3"
# patch_SpatialJoin8 = "C:\\Users\\MiguelTo\\Documents\\ArcGIS\\Default.gdb\\patch_SpatialJoin10"

# select Patches that need to be updated.


def selectdata():
    print "Beginning Data Selection."
    # make patch feature and roads layers
    print "Creating Patches Layer."
    arcpy.MakeFeatureLayer_management(patchfeatures, "patchlayer")

    # Select patches with no ROADID
    print "Select 'NULL' Patches."
    arcpy.SelectLayerByAttribute_management("patchlayer", "NEW_SELECTION", ' "ROADID" IS NULL ')
    print "Data Acquisition Completed \n"


# Spatial Join on closest road within 30'. Place in the created workspace
def joinfeature():

    print "Beginning the joining of Roads data to Patches."
    arcpy.SpatialJoin_analysis("patchlayer", joinFeatures, outputFeatures, "JOIN_ONE_TO_ONE", "KEEP_ALL", "FACILITYID \"FACILITYID\" true true false 4 Long 0 0 ,First,#,patch,FACILITYID,-1,-1;SHAPE_Length \"SHAPE_Length\" false true true 8 Double 0 0 ,First,#,patch,SHAPE_Length,-1,-1;SHAPE_Area \"SHAPE_Area\" false true true 8 Double 0 0 ,First,#,patch,SHAPE_Area,-1,-1;FACILITYID_1 \"FACILITYID\" true true false 20 Text 0 0 ,First,#,roadsSubset,FACILITYID,-1,-1;LEGACYID \"LegacyID\" true true false 20 Text 0 0 ,First,#,roadsSubset,LEGACYID,-1,-1;FACILITY_1 \"FACILITYID1\" true true false 8 Double 0 0 ,First,#,roadsSubset,FACILITY_1,-1,-1","CLOSEST", "30 Feet", "")
# Attribute Transfer Source New Patches Roads.FACILITY_1 => Patches.ROADID
    print "Data integration completed. \n"


def attributetransfer():
    fields = ['FACILITYID', 'FACILITY_1']
    cursor = arcpy.SearchCursor(outputFeatures, fields)
    index = {}
    for n in cursor:
        index[n.getValue('FACILITYID')] = int(n.getValue('FACILITY_1'))
        print index
    del cursor

    cursor = arcpy.UpdateCursor(patchfeatures)
    for n in cursor:
        print n.getValue('FACILITYID')
        if n.getValue('FACILITYID') in index:
            print index[n.getValue('FACILITYID')]
            n.setValue('ROADID', index[n.getValue('FACILITYID')])
            cursor.updateRow(n)


def UpdateFACILITYID():
    # Find the max value here, if we get nothing then quit.
    print "Create Search Cursor"
    rows = arcpy.SearchCursor(patchfeatures, "", "", "", "FACILITYID D")
    row = rows.next()
    print row
    if row == None:
        del rows
        del row
        return

    maxId = row.getValue("FACILITYID")
    # convert the id to an integer
    newId = int(maxId) + 1

    # Create update cursor for feature class, only for those features whose FACILITYID is NULL.
    rows = arcpy.UpdateCursor(patchfeatures, "FACILITYID IS NULL")

    # Now update the FACILITYIDs for those features...
    for row in rows:
        row.setValue('FACILITYID', newId)
        rows.updateRow(row)
        newId = newId + 1

    # Delete cursor and row objects to remove locks on the data
    del row
    del rows
    return


UpdateFACILITYID()
selectdata()
joinfeature()
attributetransfer()
