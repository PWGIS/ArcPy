import arcpy

arcpy.env.overwriteOutput = True

roadfeatures = "Database Connections\\A1_durham-gis.sde\\GIS_Data.A1.Road_Features\\GIS_Data.A1.Roads"
patchfeatures = "Database Connections\\PW_Tax_sql_PW.sde\\PW.PW.PatchingPolygon"
outputFeatures = r"C:\Users\MiguelTo\Documents\ArcGIS\Default.gdb\arcpyTestJoin"


def selectdata():
    # select Patches that need to be updated.
    print "Beginning Data Selection."
    # make patch feature and roads layers
    print "Creating Patches Layer."
    arcpy.MakeFeatureLayer_management(patchfeatures, "patchlayer")

    # Select patches with no ROADID
    print "Selecting 'NULL' Patches."
    arcpy.SelectLayerByAttribute_management("patchlayer", "NEW_SELECTION", ' "ROADID" IS NULL ')
    print "Data Selection Complete. \n"


# Spatial Join on closest road within 30'. Place in the created workspace
def joinfeature():
    print "Beginning the joining of Roads data to Patches."
    arcpy.SpatialJoin_analysis(patchfeatures, roadfeatures, outputFeatures, "JOIN_ONE_TO_ONE", "KEEP_ALL",
                               "FACILITYID \"FACILITYID\" true true false 4 Long 0 10 ,First,#,Database Connections\\PW_Tax_sql_PW.sde\\PW.PW.PatchingPolygon,FACILITYID,-1,-1;ROADID \"ROADID\" true true false 4 Long 0 10 ,First,#,Database Connections\\PW_Tax_sql_PW.sde\\PW.PW.PatchingPolygon,ROADID,-1,-1;FACILITYID_1 \"FACILITYID\" true true false 20 Text 0 0 ,First,#,Database Connections\\A1_durham-gis.sde\\GIS_Data.A1.Road_Features\\GIS_Data.A1.Roads,FACILITYID,-1,-1;FACILITY_1 \"FACILITYID1\" true true false 8 Double 8 38 ,First,#,Database Connections\\A1_durham-gis.sde\\GIS_Data.A1.Road_Features\\GIS_Data.A1.Roads,FACILITY_1,-1,-1",
                               "CLOSEST", "", "")
    # Attribute Transfer Source New Patches Roads.FACILITY_1 => Patches.ROADID
    print "Data join complete. \n"


def attributetransfer():
    fields = ['FACILITYID', 'FACILITY_1']
    cursor = arcpy.SearchCursor(outputFeatures, fields)
    index = {}
    for n in cursor:
        if n.getValue('FACILITY_1') is not None:
            index[n.getValue('FACILITYID')] = int(n.getValue('FACILITY_1'))
    del cursor

    cursor = arcpy.UpdateCursor(patchfeatures)
    for n in cursor:
        if n.getValue('FACILITYID') in index:
            n.setValue('ROADID', index[n.getValue('FACILITYID')])
            cursor.updateRow(n)


def UpdateFACILITYID():
    # Find the max value here, if we get nothing then quit.
    print "Create Search Cursor"
    rows = arcpy.SearchCursor(patchfeatures, "", "", "", "FACILITYID D")
    row = rows.next()
    print row
    if row is None:
        del rows
        del row
        return

    maxId = row.getValue("FACILITYID")
    if maxId is None:
        maxId = 0
    print row.getValue("FACILITYID")
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
# selectdata()
# joinfeature()
# attributetransfer()