import arcpy, time, os


def addressinparcel(feature_class, final_join):
    """ ARGS
        feature_class : The feature class that is being updated.
        final_join :    The dialog path to the join that has the feature class being updated.
                        Final Join is expected to be joined as follows;
                        Final Join must be a point feature class.
                        Feature class joined to parcels containing the feature.
                        The result being joined to parcels nearest the feature.

        ASSUMPTIONS     - The name of the field being updated is "LOCATION"

        Takes a Feature Class and updates the location field and updates
        it with the site address of the Address Point contained within the same parcel.
        If there is more than one Address Point, it will take the nearest address point to the feature.
        If there are no Address Points, it will take the site address sof the parcel."""

    # determine if feature_class is a line. if so, convert to centroid.
    if arcpy.Describe(feature_class).shapeType != "Point":
        logmessage( "Error Second Argument must be a Point Feature Class")
        return

    # create Layers; Features, Parcels, Address Points
    arcpy.MakeFeatureLayer_management(feature_class, "Feature_Layer")
    logmessage( "Feature Layer Created.")
    arcpy.MakeFeatureLayer_management("Database Connections/A1_durham-gis.sde/GIS_Data.A1.TaxData/GIS_Data.A1.Parcels",
                                      "Parcels_Layer")
    logmessage( "Parcels Layer Created.")
    arcpy.MakeFeatureLayer_management(
        "Database Connections/A1_durham-gis.sde/GIS_Data.A1.AddressFeatures/GIS_Data.A1.ActiveAddressPoints",
        "AP_Layer")
    logmessage( "Address Points Layer Created.")
    # iterate through features that are within a parcel. "PARCEL_ID IS NOT NULL"
    with arcpy.da.SearchCursor(final_join, ["Parcel_ID", "PARCEL_ID_1", "FACILITYID"],
                               where_clause='PARCEL_ID IS NOT NULL') as cursor:
        for row in cursor:
            # select that parcel
            arcpy.SelectLayerByAttribute_management("Parcels_Layer", "NEW_SELECTION", "[PARCEl_ID] = " + str(row[0]))
            # Select APs within the selected parcel
            arcpy.SelectLayerByLocation_management("AP_Layer", "WITHIN", "Parcels_Layer")
            transcribe(str(row[0]) + " Parcel contains " + str(arcpy.GetCount_management("AP_Layer")) + " Address Point(s)")
            # If AP Count is 1, move the AP Address to the feature.
            if int(arcpy.GetCount_management("AP_Layer")[0]) == 1:
                arcpy.SelectLayerByAttribute_management("Feature_Layer", "NEW_SELECTION",
                                                        "[FACILITYID] = '" + str(row[2]) + "'")
                logmessage("\tTransferring Address to swNode " + str(row[2]))
                transcribe("\tTransferring Address to swNode " + str(row[2]))
                ap_cursor = arcpy.da.SearchCursor("AP_Layer", ["SITE_ADDRE"])
                for AP in ap_cursor:
                    transcribe("\t" + AP[0])
                    arcpy.CalculateField_management("Feature_Layer", "LOCATION", "\"" + AP[0] + "\"", "", "")
                del ap_cursor
            # If AP Count is > 1,
            # Create a spatial join using selected feature and selected address points, then choose the nearest one
            elif int(arcpy.GetCount_management("AP_Layer")[0]) > 1:
                arcpy.SpatialJoin_analysis("Feature_Layer", "AP_Layer", "in_memory/NearestAP", "JOIN_ONE_TO_ONE",
                                           "KEEP_ALL", "", "CLOSEST")
                arcpy.MakeFeatureLayer_management("in_memory/NearestAP", "NearestAP_Layer")
                transcribe("\tTransferring Address to swNode " + str(row[2]))
                ap_cursor = arcpy.da.SearchCursor("NearestAP_Layer", ["SITE_ADDRE"])
                for AP in ap_cursor:
                    transcribe("\t" + AP[0])
                    arcpy.CalculateField_management("Feature_Layer", "LOCATION", "\"" + AP[0]+ "\"", "", "")
                del ap_cursor
            # If AP Count == 0, move the Parcel's Site Address to the feature
            elif int(arcpy.GetCount_management("AP_Layer")[0]) == 0:
                arcpy.SelectLayerByAttribute_management("Feature_Layer", "NEW_SELECTION",
                                                        "[FACILITYID] = '" + str(row[2]) + "'")
                transcribe("\tTransferring Address to swNode " + str(row[2]))
                parcel_cursor = arcpy.da.SearchCursor("Parcel_Layer", ["SITE_ADDRE"])
                for parcel in parcel_cursor:
                    transcribe("\t" + parcel[0])
                    arcpy.CalculateField_management("Feature_Layer", "LOCATION", "\"" + parcel[0] + "\"", "", "")
                del parcel_cursor


def createLayers(layers):
    # Loop through feature dataset once and compare it to each item in the list
    if type(layers) is str:
        print "Is a string"
        for fds in arcpy.ListDatasets('', 'Feature'):
            for fc in arcpy.ListFeatureClasses('', '', fds):
                if str.lower(layers) == str.lower(str(fc.split('.')[-1])):
                    # arcpy.MakeFeatureLayer_management(arcpy.env.workspace + "/" + fds + "/" + fc, layers + "lyr")
                    return layers + "lyr"
        else:
            print "No feature class found matching input: " + layers

    elif type(layers) is list:
        # convert all items in list to lowercase in order to avoid case errors.
        layers = [item.lower() for item in layers]
        lyrList = []
        # iterate through FDS and FCs
        for fds in arcpy.ListDatasets('', 'Feature'):
            for fc in arcpy.ListFeatureClasses('','', fds):
                if any(str.lower(str(fc.split('.')[-1])) == layer for layer in layers):
                    print "Found " + fc
                    # arcpy.MakeFeatureLayer_management(arcpy.env.workspace + "/" + fds + "/" + fc, layers + "lyr")
                    lyrList.append(str.lower(str(fc.split('.')[-1]) + "lyr"))
                    if len(lyrList) == len(layers):
                        return lyrList
        else:
            # print incorrect input name
            if len(lyrList) == 0:
                print "0 items in the input data matched with feature classes."
                return
            else:
                lyrCheck = [x.replace('lyr', '') for x in lyrList]
                print str(len(layers) - len(lyrList)) + " feature class(es) were not found."
                print list(set(layers) - set(lyrCheck))
                return lyrList


def logmessage(message):
    """ARGS:
    message: a string variable to be written to the file and console

    DESCRIPTION:
    Function writes the STRING argument to the console.
    String also prepends the argument with a time stamp."""
    print time.strftime ("%H:%M", time.localtime()) + "\t" + str(message)
    return


def transcribe(message, _filepath=os.path.dirname(__file__) + "/"):
    """ ARGS:
    message: a string variable to be written to the file and console
    _filepath: the location of the directory to write the file to, assumes '/' notation
        default location is the same directory that the program is being run from.

    DESCRIPTION:
    Function writes the STRING argument out to a text file and console.
    The file name is the name of the program plus the date that it is run.
    The file_path defaults to the directory of the program being run.
    Adding a file_path STRING argument will overwrite the defaults

    DEPENDENCIES:
    Utilizes the logmessage function to write to console.
    """
    txt_file = open(_filepath + os.path.splitext(os.path.basename(__file__))[0] +
                    "_" + time.strftime("%Y-%m-%d", time.localtime()) + ".txt", "a")
    txt_file.write(time.strftime("%H:%M", time.localtime()) + "\t" + str(message) + "\n")
    logmessage(message)
    txt_file.close()


def updatefacilityid(featurelayer):
    """ ARGS:
    featurelayer: A reference to a layer that contains the featureclass that has to be updated.

    DESCRIPTION:
    Function takes in a feature layer and isolates the highest FACILITYID value.
    Then it searches for records with a FACILITYID of NULL and then updates them
        in sequential order."""
    # Find the max value here, if we get nothing then quit.
    print "Create Search Cursor"
    rows = arcpy.SearchCursor(featurelayer, "", "", "", "FACILITYID D")
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
    del rows


def versionLayers(layers, parent = arcpy.Describe(arcpy.env.workspace).connectionProperties.version):
    """

    """
    # check if version to be created exists first. Skip if that is the case.
    if type(layers) is not list:
        print "Argument must be a list of layer names"
        return
    print "Print Arguments: " + layers, parent
    for i, version in enumerate(arcpy.da.ListVersions(arcpy.env.workspace)):
        print i, version.name
        verName = os.path.splitext(os.path.basename(__file__))[0] + time.strftime("_%m-%d", time.localtime())
        if version.name == "PUBLICWORKS." + verName:
            logmessage ("Version already exists. Skipping version creation.")
            break
        elif i == len(arcpy.da.ListVersions(arcpy.env.workspace)) - 1:
            logmessage("Version Not Found. Creating Version[" + verName + "]")
            arcpy.CreateVersion_management(arcpy.env.workspace, parent, verName, "PROTECTED")
    verName = "PUBLICWORKS." + verName
    # Process data
    # Check if data is a layer name or a list of layers
    if type(layers) is str:
        arcpy.ChangeVersion_management(layers, "TRANSACTIONAL", verName)
        print "Version Updated for " + layers
    elif type(layers) is list:
        for layer in layers:
            arcpy.ChangeVersion_management(layer, "TRANSACTIONAL", verName)
        print "Version Updated for " + layers
    return verName





if __name__ == "__main__":
    logmessage("is this working?")
    transcribe(2+3)
