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
    # feature_class = "Database Connections/publiworks_TAX_SQL_Miguelto.sde/Publicworks.PUBLICWORKS.swNodes"
    # final_join = "H:/Work/swNodes20180420.gdb/JoinFinal"
    # determine if feature_class is a line. if so, convert to centroid.
    file = open("H:/Work/Report" + today + ".txt", "w")
    if arcpy.Describe(feature_class).shapeType != "Point":
        LogMessage( "Error Second Argument must be a Point Feature Class")
        return

    # create Layers; Features, Parcels, Address Points
    arcpy.MakeFeatureLayer_management(feature_class, "Feature_Layer")
    LogMessage( "Feature Layer Created.")
    arcpy.MakeFeatureLayer_management("Database Connections/A1_durham-gis.sde/GIS_Data.A1.TaxData/GIS_Data.A1.Parcels",
                                      "Parcels_Layer")
    LogMessage( "Parcels Layer Created.")
    arcpy.MakeFeatureLayer_management(
        "Database Connections/A1_durham-gis.sde/GIS_Data.A1.AddressFeatures/GIS_Data.A1.ActiveAddressPoints",
        "AP_Layer")
    LogMessage( "Address Points Layer Created.")
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
                print "\tTransferring Address to swNode " + str(row[2])
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


def logmessage( message):
    """ARGS:
    message: a string variable to be written to the file and console

    DESCRIPTION:
    Function writes the STRING argument to the console.
    String also prepends the argument with a time stamp."""
    print time.strftime ("%H:%M", time.localtime()) + "\t" + message
    return


def transcribe(message, file_path = os.path.dirname(__file__)+ "/"):
    """ ARGS:
    message: a string variable to be written to the file and console
    file_path: the location of the directory to write the file to, assumes '/' notation
        default location is the same directory that the program is being run from.

    DESCRIPTION:
    Function writes the STRING argument out to a text file and console.
    The file name is the name of the program plus the date that it is run.
    The file_path defaults to the directory of the program being run.
    Adding a file_path STRING argument will overwrite the defaults

    DEPENDENCIES:
    Utilizes the logmessage function to write to console.
    """

    txt_file = open(file_path + os.path.basename(__file__).replace(".py",
                    "_" + time.strftime("%Y-%m-%d",time.localtime()) + ".txt"), "a")
    txt_file.write(time.strftime("%H:%M", time.localtime()) + "\t" + message + "\n")
    logmessage(message)
    txt_file.close()


def updatefacilityid(featurelayer):
    """ ARGS:
    featurelayer: A reference to a layer that contains the featureclass that has to be updated.

    DESCRIPTION:
    Function takes in a feature layer and isolates the highest FACILITYID value.
    Then it searches for records with a FACILITYID of NULL and then updates them
        in sequential order.
        """
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


if __name__ == "__main__":
    logmessage("is this working?")
