import arcpy

arcpy.env.overwriteOutput = True
# Be sure that roadfeatures and patchfeatures are connecting through your established database connections.

roadfeatures = "Database Connections\\A1_durham-gis.sde\\GIS_Data.A1.Road_Features\\GIS_Data.A1.Roads"
patchfeatures = "Database Connections\\PW_Tax_sql_PW.sde\\PW.PW.PatchingPolygon"
outputFeatures = "in_memory/tempJoin"


# A method that updates the FACILITYID for new patch polygons. It checks for the highest existing integer value and then
# Takes the next number and begins updating each NULL FACILITYID incrementing by 1.


def BackupData():
    print "Beginning data backup..."
    try:
        arcpy.Copy_management(patchfeatures, "D:/BackupRepo.gdb/patches" + time.strftime("%Y%m%d", time.localtime()))
        print "Data backup completed.\n"
    except Exception:
        pass


def UpdateFACILITYID():
    # Find the max value here, if we get nothing then quit.
    print "Create Search Cursor"
    rows = arcpy.SearchCursor(patchfeatures, "", "", "", "FACILITYID D")
    row = rows.next()
    if row is None:
        del rows
        del row
        return

    maxId = row.getValue("FACILITYID")
    if maxId is None:
        maxId = 0
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


def selectdata():
    # select Patches that need to be updated.
    print "Beginning Data Selection."
    # make patch feature layers
    arcpy.MakeFeatureLayer_management(patchfeatures, "patchlayer")
    # Select patches with no ROADID, i.e. a value of NULL
    arcpy.SelectLayerByAttribute_management("patchlayer", "NEW_SELECTION", ' "ROADID" IS NULL ')
    print "Data Selection Complete. \n"


# Spatial Join on closest road within 30'. Place in the created workspace
def joinfeature():
    print "Beginning join, Patches : Roads"
    # Uses Spatial Join to create a feature class of the each selected patch and it's closest road
    # Attributes are: FACILITID (Patch FACILITYID), FACILITYID_1 (Roads FACILITYID [string]), FACILITY_1 (Roads FACILITYID INT)
    arcpy.SpatialJoin_analysis(patchfeatures, roadfeatures, outputFeatures, "JOIN_ONE_TO_ONE", "KEEP_ALL",
                               "FACILITYID \"FACILITYID\" true true false 4 Long 0 10 ,First,#,Database Connections\\PW_Tax_sql_PW.sde\\PW.PW.PatchingPolygon,FACILITYID,-1,-1;ROADID \"ROADID\" true true false 4 Long 0 10 ,First,#,Database Connections\\PW_Tax_sql_PW.sde\\PW.PW.PatchingPolygon,ROADID,-1,-1;FACILITYID_1 \"FACILITYID\" true true false 20 Text 0 0 ,First,#,Database Connections\\A1_durham-gis.sde\\GIS_Data.A1.Road_Features\\GIS_Data.A1.Roads,FACILITYID,-1,-1;FACILITY_1 \"FACILITYID1\" true true false 8 Double 8 38 ,First,#,Database Connections\\A1_durham-gis.sde\\GIS_Data.A1.Road_Features\\GIS_Data.A1.Roads,FACILITY_1,-1,-1",
                               "CLOSEST", "", "")
    # Attribute Transfer Source New Patches Roads.FACILITY_1 => Patches.ROADID
    print "Data join complete. \n"


def attributetransfer():
    # The method here is that we are going to create a dictionary structure to migrate the values to the featureclass
    # Dictionary: KEY = FACILITYID (Patch FacilityID), Value = FACILITY_1 (road FacilityID)
    # Create a search cursor that only sees these two fields
    fields = ['FACILITYID', 'FACILITY_1']
    cursor = arcpy.SearchCursor(outputFeatures, fields)

    # Create the dictionary
    index = {}

    # Begin Assigning the Key:Value pair
    for n in cursor:
        if n.getValue('FACILITY_1') is not None:
            index[n.getValue('FACILITYID')] = int(n.getValue('FACILITY_1'))
    del cursor

    # Take the created dictioanry and cycle through the selected patch features
    # LOGIC | On Row: ROADID = Value of Dictionary where Key is the row's FACILITYID
    cursor = arcpy.UpdateCursor(patchfeatures)
    for n in cursor:
        if n.getValue('FACILITYID') in index:
            n.setValue('ROADID', index[n.getValue('FACILITYID')])
            cursor.updateRow(n)


BackupData()
UpdateFACILITYID()
selectdata()
joinfeature()
attributetransfer()
