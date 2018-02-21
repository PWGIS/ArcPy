import arcpy

# arcpy.env.workspace = "D:/Test.gdb"
arcpy.env.workspace = r"C:\Users\MiguelTo\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\PW_Tax_sql_PW.sde"
arcpy.env.overwriteOutput = True
#
# roadfeatures = "D:/Test.gdb/roadsSubset"
roadfeatures = r"C:\Users\MiguelTo\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\A1_durham-gis.sde\GIS_Data.A1.Road_Features\GIS_Data.A1.Roads"
# patchfeatures = "D:/Test.gdb/patch"
patchfeatures = r"C:\Users\MiguelTo\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\PW_Tax_sql_PW.sde\PW.PW.PatchingPolygon"

#joinFeatures = r"D:\Test.gdb\roadsSubset"
#targetFeatures = r"D:\Test.gdb\patch"
outputFeatures = r"D:\Test.gdb\PatchSJPoly3"
# outputFeatures = r"in_memory\tempFeatures"
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

def testdata():
    fields = ['FACILITYID', 'ROADID']
    with arcpy.da.SearchCursor("patchlayer", fields) as cursor:
        for row in cursor:
            print('{0}, {1}'.format(row[0], row[1]))
# Spatial Join on closest road within 30'. Place in the created workspace
def joinfeature():
    print "Beginning the joining of Roads data to Patches."
    # Process: Spatial Join
    patch = "patchlayer"
    GIS_Data_A1_Roads = "GIS_Data.A1.Roads"
    patch_SpatialJoin10 = "C:\\Users\\MiguelTo\\Documents\\ArcGIS\\Default.gdb\\patch_SpatialJoin10"
    arcpy.SpatialJoin_analysis(patch, roadfeatures, patch_SpatialJoin10, "JOIN_ONE_TO_ONE", "KEEP_ALL",
                               "FACILITYID \"FACILITYID\" true true false 4 Long 0 0 ,First,#,patch,FACILITYID,-1,-1;ROADID \"ROADID\" true true false 4 Long 0 0 ,First,#,patch,ROADID,-1,-1;FACILITYID_1 \"FACILITYID\" true true false 20 Text 0 0 ,First,#,GIS_Data.A1.Roads,FACILITYID,-1,-1;FACILITY_1 \"FACILITYID1\" true true false 8 Double 8 38 ,First,#,GIS_Data.A1.Roads,FACILITY_1,-1,-1",
                               "CLOSEST", "100 Feet", "")

# Attribute Transfer Source New Patches Roads.FACILITY_1 => Patches.ROADID
    print "Data integration completed. \n"


def attributetransfer():
    fields = ['FACILITYID_1', 'FACILITY_1']
    # cursor = arcpy.SearchCursor(outputFeatures, fields)
    # index = {}
    with arcpy.SearchCursor(outputFeatures, fields) as cursor:
        for row in cursor:
            print('{0}, {1}'.format(row[0], row[1]))

    # for n in cursor:
    #     index[n.getValue('FACILITYID')] = int(n.getValue('FACILITY_1'))
    #     print index
    # del cursor
    #
    # cursor = arcpy.UpdateCursor(patchfeatures)
    # for n in cursor:
    #     print n.getValue('FACILITYID')
    #     if n.getValue('FACILITYID') in index:
    #         print index[n.getValue('FACILITYID')]
    #         n.setValue('ROADID', index[n.getValue('FACILITYID')])
    #         cursor.updateRow(n)


def UpdateFACILITYID():
    # Find the max value here, if we get nothing then quit.
    print "Create Search Cursor"
    rows = arcpy.SearchCursor(patchfeatures, "", "", "", "FACILITYID D")
    row = rows.next()
    if row == None:
        del rows
        del row
        return

    maxId = row.getValue("FACILITYID")
    print row.getValue("FACILITYID")
    # if maxId is None:
    #     maxId = 0

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


# UpdateFACILITYID()
selectdata()
joinfeature()
# testdata()
# attributetransfer()
