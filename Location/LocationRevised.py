# MODULE IMPORT
import arcpy,  time, PWLIB

# GLOBAL VARIABLES
arcpy.env.overwriteOutput = True
PWConnection = "PUBLICWORKS-PUBLICWORKS.sde"
A1Connection = "DURHAM-GIS_A1.sde"
arcpy.env.workspace = PWConnection
thisWorkspace = arcpy.env.workspace
versionName = "LocationTest" + time.strftime("%Y%m%dT%H%M", time.localtime())


def main():
    # createLayers("SewerSystem", "Feature Dataset")
    # createLayers(["wnClearWell", "wnSamplingStation", "snControlValve"], "List")
    layers = createLayers("snCleanOut", "Feature Class")
    changeLayerVersion("PUBLICWORKS.PublicWorks_Sandbox", layers)
    FeatureInParcel(layers)
    # FeatureNearParcel(layers)
    cleanUp("PUBLICWORKS.PublicWorks_Sandbox", layers)


def changeLayerVersion(parentVersion, layers):
    """
    Creates a new version and transfers the layers to the new version.

    Loop through one list and switch to the new version.
    Loop through the second list and update the version.

    PARAMETERS
    parentVersion (string): version that the layers were initially built from.
    layers (list): Layers is now a list of lists based on the specific name of the location field.
    """

    PWLIB.logmessage("Beginning changeLayerVersion()")
    arcpy.CreateVersion_management(thisWorkspace, parentVersion, versionName, "PROTECTED")
    PWLIB.logmessage("\tChanging version to " + versionName + "...")
    i = 0
    layerCount = len(layers)
    while i < layerCount:
        for fc in layers[i]:
            layer = fc + "Layer"
            arcpy.ChangeVersion_management(layer, "TRANSACTIONAL", "PUBLICWORKS." + versionName, "")
        i += 1  # shorthand for saying i = i + 1
    PWLIB.logmessage("changeLayerVersion() complete.\n")


def cleanUp(parentVersion, layers):
    """
    Reverts layers to parent version and deletes the processing version.

    PARAMETERS:
    parentVersion (string): The version the data will be posted to.
    layers (list): List of layers that were used for processing.
    """
    PWLIB.logmessage("Beginning Version Clean Up.")
    i = 0
    layerCount = len(layers)
    while i < layerCount:
        if i == 0 and len(layers[i]) > 0:
            PWLIB.logmessage("\tConverting Location Layers")
        elif i == 1 and len(layers[i]) > 0:
            PWLIB.logmessage("\tConverting Location Description Layers")

        for fc in layers[i]:
            layer = fc + "Layer"
            arcpy.ChangeVersion_management(layer, "TRANSACTIONAL", parentVersion, "")
            # Reconcile and post version.
            PWLIB.logmessage("\tReconciling/Posting version (" + versionName + ") to parent (" + parentVersion + ")")
            arcpy.ReconcileVersions_management(thisWorkspace, "ALL_VERSIONS", parentVersion, "PUBLICWORKS." +
                                               versionName,  "LOCK_ACQUIRED", "ABORT_CONFLICTS", "BY_OBJECT",
                                               "FAVOR_EDIT_VERSION", "POST", "DELETE_VERSION")
        i += 1  # shorthand for saying i = i + 1
    PWLIB.logmessage("Finished Reconciling/Posting all layers\n")


def createLayers(OriginalData, DataType):
    """ Creates layers for the feature classes in a feature dataset, a feature class, or a list of feature classes

    We only make layers for point feature classes with a "location" field that are not part of an abandoned
    feature class nor are they part of the county-maintained sewer data.  We will have to address the fact that some
    feature datasets may include feature classes, like soScadaSensor that we do not want to process.

    PARAMETERS:
        OriginalData (Variable): Data provided to be processed for layer creation.
        DataType (String): Indicates what the data type is (feature dataset, feature class, or list).

    RETURN:
        list[list, list]: A list containing the names of the layers created and separated by field
        [LOCATION, LOCATIONDESCRIPTION]"""

    PWLIB.logmessage("Entering Function: Create Layers.")
    
    # the list that will hold the names of the feature classes.  because the location field is not consistent across all
    # the feature classes layerList is actually a list of lists, where the first list, locationList, holds all the
    # feature classes where the field name is LOCATION and the second list, descriptionList, holds all the feature
    # classes where the field name is LOCATIONDESCRIPTION.
    layerList = []
    locationList = []
    descriptionList = []

    if DataType == "Feature Dataset":
        PWLIB.logmessage("\tProcessing Feature Dataset.")
        datasets = arcpy.ListDatasets('', 'Feature')
        for fds in datasets:
            shortName = fds.split(".")[2]
            # the fullname of a feature class on sde includes the name of the database
            # (PUBLICWORKS.publicworks.snCleanout") so the split method allows us to access the actual
            # feature class name
            if shortName == OriginalData:
                # Once you have found the correct dataset you want to loop through the feature classes.  we then set
                # three additional criteria:
                # 1. it needs to be a point feature class because lines can cross multiple parcels and their location i
                #   really based on the point structures they connect to;
                # 2. it should not be part of the county-maintained sewer infrastructure (only valid for sanitary sewer)
                # 3. it should not be part of the abandoned feature class, which is really a static dataset that should
                #   not be routinely updated aside from adding in new abandoned featues.
                for fc in arcpy.ListFeatureClasses('', '', fds):
                    if arcpy.Describe(fc).shapeType == "Point":
                        newName = fc.split(".")[2]
                        if newName.endswith("COUNTY") == False and newName.startswith("Abnd") == False:
                            fields = arcpy.ListFields(fc)
                            # loop through the field names and confirm that there is a location field associated with
                            # the feature class. Since there can exist one of two location fields, and we will need to
                            # know the name of the location field later, use if/elif to determine the correct field
                            # name and then create the feature layer only for those features where the value in that
                            # field is null.
                            # The name of the created layer is appended into a list based on the field name.
                            for field in fields:
                                fieldName = str(field.name)
                                if fieldName == "LOCATION":
                                    arcpy.MakeFeatureLayer_management(thisWorkspace + "/" + fds + "/" + fc,
                                                                      newName + "Layer", fieldName + " IS NULL")
                                    locationList.append(newName)
                                    break
                                elif fieldName == "LOCATIONDESCRIPTION":
                                    arcpy.MakeFeatureLayer_management(thisWorkspace + "/" + fds + "/" + fc,
                                                                      newName + "Layer", fieldName + " IS NULL")
                                    descriptionList.append(newName)
                                    break
                # the locationList and descriptionList lists are then appended to the layerList list
                layerList.append(locationList)
                layerList.append(descriptionList)
                PWLIB.logmessage("\tOutput Returned: " + str(layerList) + "\n")
                return layerList

    elif DataType == "Feature Class":
        # if a single feature class is passed to the function, we use the ListDatasets and ListFeatureClasses to find it
        PWLIB.logmessage("\tProcessing Feature Class.")
        PWLIB.logmessage("\tData Provided: " + str(OriginalData))
        datasets = arcpy.ListDatasets('', 'Feature')
        for fds in datasets:
            for fc in arcpy.ListFeatureClasses('', '', fds):
                newName = fc.split(".")[2]
                # the full name of an SDE feature class includes the owner, so we use the split method to parse just the
                # actual feature #class name and then compare that to the feature class name passed to the function.
                if newName == OriginalData:
                    PWLIB.logmessage("\tLocated " + newName)
                    if arcpy.Describe(fc).shapeType == "Point":
                        fields = arcpy.ListFields(fc)
                        # Search for correct location field. Make a feature layer. Append the feature class to the list
                        for field in fields:
                            fieldName = str(field.name)
                            if fieldName == "LOCATION":
                                arcpy.MakeFeatureLayer_management(thisWorkspace + "/" + fds + "/" + fc,
                                                                  newName + "Layer", fieldName + " IS NULL")
                                locationList.append(newName)
                                break
                            elif fieldName == "LOCATIONDESCRIPTION":
                                arcpy.MakeFeatureLayer_management(thisWorkspace + "/" + fds + "/" + fc,
                                                                  newName + "Layer", fieldName + " IS NULL")
                                descriptionList.append(newName)
                                break
                        # append the locationList and the descriptionList to the layerList and return the layerList
                        layerList.append(locationList)
                        layerList.append(descriptionList)
                        PWLIB.logmessage("\tOutput Returned: " + str(layerList) + "\n")
                        return layerList

    elif DataType == "List":
        # Loop through feature dataset once and compare it to each item in the list
        PWLIB.logmessage("\tProcessing Feature List.")
        checkCount = 0
        datasets = arcpy.ListDatasets('', 'Feature')
        for fds in datasets:
            for fc in arcpy.ListFeatureClasses('', '', fds):
                newName = fc.split(".")[2]
                if newName in OriginalData:
                    PWLIB.logmessage("\t" + newName + " located.")
                    fields = arcpy.ListFields(fc)
                    # Search for correct location field, make  feature layer,  append  feature layer to the correct list
                    for field in fields:
                        fieldName = str(field.name)
                        if fieldName == "LOCATION":
                            arcpy.MakeFeatureLayer_management(thisWorkspace + "/" + fds + "/" + fc,
                                                              newName + "Layer", fieldName + " IS NULL")
                            locationList.append(newName)
                            checkCount += 1
                            break
                        elif fieldName == "LOCATIONDESCRIPTION":
                            arcpy.MakeFeatureLayer_management(thisWorkspace + "/" + fds + "/" + fc,
                                                              newName + "Layer", fieldName + " IS NULL")
                            descriptionList.append(newName)
                            checkCount += 1
                            break
                if checkCount >= len(OriginalData):
                    layerList.append(locationList)
                    layerList.append(descriptionList)
                    PWLIB.logmessage("\tOutput Returned: " + str(layerList) + "\n")
                    return layerList
        if len(locationList) + len(descriptionList) < len(OriginalData):
            MissingData = []
            for item in OriginalData:
                if item not in locationList and item not in descriptionList:
                    MissingData.append(item)
                    print "ERROR: Feature classes were not found for following inputs " + str(MissingData)

    # Check to see if any layers were created.
    if len(locationList) == 0 and len(descriptionList) == 0:
        print "Error: No feature classes were found matching the provided inputs."
        quit()

    layerList.append(locationList)
    layerList.append(descriptionList)
    print layerList
    return layerList
        

def FeatureInParcel(layerList):
    """
    Assigns the address of the nearest address point within the parcel which the feature is contained.

    Loop through the lists and use the spatial join to create an in-memory feature class (joinWithin) between the layer
    and the parcel layer where the layer feature sits within a parcel. We use da.SearchCursor to iterate through
    joinWithin, extracting the parcelID, facilityID, and site address.  Using Select by Attributes we find any address
    points with the same parcel. If there is only one address point, we calculate its site address into the layer's
    location field.  If there is more than one address point that matches, we do a second in-memory join to find the
    address point that is nearest the selected feature and calculate that site address into the location field.  If
    there is no address point we use the parcel site address for the location field.

    PARAMETERS:
        layerList (list): a list containing two lists of layers to be addressed.
    """

    # first make the address point layer
    PWLIB.logmessage("Beginning updates for features in parcels.")
    AddressPoints = A1Connection + "/GIS_Data.A1.AddressFeatures/GIS_Data.A1.ActiveAddressPoints"
    arcpy.MakeFeatureLayer_management(AddressPoints, "AP_Layer")

    Parcels = A1Connection + "/GIS_Data.A1.TaxData/gis_data.A1.Parcels"

    # layerlist is now a list of list, with the first list layerList[0] representing those feature classes where the
    # field name is "LOCATION" and layerList[1] includes feature classes where the field name is "LOCATIONDESCRIPTION"
    i = 0
    for list in layerList:
        if i == 0:
            locationfield = "LOCATION"
        else:
            locationfield = "LOCATIONDESCRIPTION"

        for fc in layerList[i]:
            layer = fc + "layer"
            joinWithin = "in_memory/joinWithin" + fc
            arcpy.SpatialJoin_analysis(layer, Parcels, joinWithin, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "",
                                       "COMPLETELY_WITHIN", "", "")
            count = 0
            result = arcpy.GetCount_management(joinWithin)
            if result > 0:
                # iterate through features that are within a parcel. "PARCEL_ID IS NOT NULL"
                with arcpy.da.SearchCursor(joinWithin, ["Parcel_ID", "FACILITYID", "SITE_ADDRE"]) as cursor:
                    for row in cursor:
                        # select the address points with the same parcel ID
                        arcpy.SelectLayerByAttribute_management("AP_Layer", "NEW_SELECTION", "[PARCEl_ID] = " + str(row[0]))
                        # Select APs within the selected parcel
                        # If AP Count is 1, move the AP Address to the feature.
                        if int(arcpy.GetCount_management("AP_Layer")[0]) == 1:
                            arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION",
                                                                    "[FACILITYID] = '" + str(row[1]) + "'")
                            # layerResult = arcpy.GetCount_management(layer)
                            # layerCount = int(layerResult.getOutput(0))
                            PWLIB.logmessage("\tTransferring Address to layer " + str(row[1]))
                            ap_cursor = arcpy.da.SearchCursor("AP_Layer", ["SITE_ADDRE"])
                            for AP in ap_cursor:
                                arcpy.CalculateField_management(layer, locationfield, "\"" + AP[0] + "\"", "", "")
                            del ap_cursor
                        # If AP Count is > 1,
                        # Create spatial join using selected feature and selected address points. choose the nearest one
                        elif int(arcpy.GetCount_management("AP_Layer")[0]) > 1:
                            arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION",
                                                                    "[FACILITYID] = '" + str(row[1]) + "'")
                            # layerResult = arcpy.GetCount_management(layer)
                            # layerCount = int(layerResult.getOutput(0))
                            # print layerCount
                            arcpy.SpatialJoin_analysis(layer, "AP_Layer", "in_memory/NearestAP", "JOIN_ONE_TO_ONE",
                                                       "KEEP_ALL", "", "CLOSEST")
                            arcpy.MakeFeatureLayer_management("in_memory/NearestAP", "NearestAP_Layer")
                            PWLIB.logmessage("\tTransferring Address to swNode " + str(row[1]))
                            ap_cursor = arcpy.da.SearchCursor("NearestAP_Layer", ["SITE_ADDRE"])
                            for AP in ap_cursor:
                                arcpy.CalculateField_management(layer, locationfield, "\"" + AP[0] + "\"", "", "")
                            del ap_cursor
                        # If AP Count == 0, move the Parcel's Site Address to the feature
                        elif int(arcpy.GetCount_management("AP_Layer")[0]) == 0:
                            arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION",
                                                                    "[FACILITYID] = '" + str(row[1]) + "'")
                            # layerResult = arcpy.GetCount_management(layer)
                            # layerCount = int(layerResult.getOutput(0))
                            arcpy.CalculateField_management(layer, locationfield, "\"" + str(row[2]) + "\"", "", "")
                            # print layerCount
                        count += 1
                        if count >= 10:
                            return
        i = i + 1
    # FeatureNearParcel(layerList)


def FeatureNearParcel(layerList):
    """
    After running FeatureInParcel(), function calculates addresses nearest to features outside of parcels.

    This function  is run after the FeatureInParcel function and is used to calculate a location for those features that
    do not sit within a parcel.  The first step is to do a new select by attribute query to select ONLY those features
    that still have a null value in the location field.  Next we do a spatial join with the parcel layer to identify the
    closest parcel. A search cursor is then used to iterate through the resulting in-memory feature class and the site
    adddress value is returned and used to calculate the value of the individual feature.

    PARAMETERS:
        layerList (list): a list containing two lists of layers to be addressed.

    NOTE:
        Function must be run after FeatureNearParcel().
    """
    PWLIB.logmessage("Beginning FeatureNearParcel().")
    # first make the address point layer
    AddressPoints = A1Connection + "/GIS_Data.A1.AddressFeatures/GIS_Data.A1.ActiveAddressPoints"
    arcpy.MakeFeatureLayer_management(AddressPoints, "AP_Layer")
    Parcels = A1Connection + "/GIS_Data.A1.TaxData/gis_data.A1.Parcels"

    # layerlist is now a list of list, with the first list layerList[0] representing those feature classes where the field name is "LOCATION" and
    # layerList[1] includes feature classes where the field name is "LOCATIONDESCRIPTION".
    print layerList
    print len(layerList)
    i = 0
    for list in layerList:
        if i == 0:
            locationfield = "LOCATION"
        else:
            locationfield = "LOCATIONDESCRIPTION"

        for fc in layerList[i]:
            layer = fc + "Layer"
            joinClosest = "in_memory/joinClosest" + fc
            arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", "[" + locationfield + "] IS NULL")
            arcpy.SpatialJoin_analysis(layer, Parcels, joinClosest, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "", "CLOSEST", "","")
            result = arcpy.GetCount_management(joinClosest)
            arcpy.AddJoin_management(layer, "OBJECTID", joinClosest, "TARGET_FID", "KEEP_ALL")

            if result > 0:
                arcpy.CalculateField_management(layer, locationfield, "[joinClosest" + fc + ".SITE_ADDRE]", "VB", )
            PWLIB.logmessage("\t" + fc + " Calculated")
        i += 1  # shorthand for saying i = i + 1

    return


if __name__ == '__main__':
    main()
