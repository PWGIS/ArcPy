

# Import arcpy and other modules
import arcpy,  time, PWLIB

#i used todayhhmm to create the version below, but we can handle this differently and avoid setting it globally
today = time.strftime("%Y%m%d", time.localtime())
todayhhmm = time.strftime("%Y%m%dT%H%M", time.localtime())

#if the data already exists it will be overwritten
arcpy.env.overwriteOutput = True

#SDE connections
PWConnection = "PUBLICWORKS-PUBLICWORKS.sde" #building off my version for testing
A1Connection = "DURHAM-GIS_A1.sde"

#we use the workspace in the changeLayerVersion function, but could we just set it there?
arcpy.env.workspace = PWConnection
thisWorkspace = arcpy.env.workspace


#all functions are called from main
def main():

    #set the locally-declared variable "layerList" to the function createLayers so you can access them throughout main

    # layerList = createLayers("SewerSystem", "Feature Dataset")
    #layerList = createLayers(["wnClearWell", "wnSamplingStation"], "List")
    layerList = createLayers(["wnCldearWell", "wnSamplingStation", "snControlValve"], "List")

    # layerList = createLayers("snnSystemValve", "Feature Class")

    # changeLayerVersion("Seando.UTIL_EDITS", layerList)

    # FeatureInParcel(layerList)

    # return

'''creates a new version and transfers the layers to the new version.  layers is now a list of lists based on the specific
    name of the location field, so below we need to loop through one list and switch to the new version then
    loop through the second list and update the version''' 
def changeLayerVersion(parentVersion, layers):

    PWLIB.logmessage("******STARTING*******")

    #versionName =  steal from transcribe
    # Create Version
    arcpy.CreateVersion_management(thisWorkspace, parentVersion, versionName, "PROTECTED")
    PWLIB.logmessage(" Version created.")

# Switch all the layers you created in the createLayers function to the newly-created version
    PWLIB.logmessage("Changing version to " + versionName + "...")
    i = 0
    layerCount = len(layers)
    print layerCount
    while i < layerCount:
        for fc in layers[i]:
            layer = fc + "Layer"
            print layer
            arcpy.ChangeVersion_management(layer, "TRANSACTIONAL", "Seando." + versionName, "")
	i = i+1
		
    PWLIB.logmessage("Done.")

    return

''' Creates layers for the feature classes in the feature dataset, single feature class, or a group of feature classes provided in a list.  the
two arguments are the data you are passing in and then what type of data it is (feature dataset, feature class, or list).  The function handles each
data type differently.  We only make layers for point feature classes with a "location" field that are not part of an abandoned
feature class nor are they part of the county-maintained sewer data.  We will have to address the fact that some feature datasets may include
feature classes, like soScadaSensor that we do not want to process. '''
def createLayers(OriginalData, DataType):

    #the workspace is set globally so i don't think it needs to be set here.  Pick one!
    arcpy.env.workspace = PWConnection

    PWLIB.logmessage("Start the create layers function...")
    
    #the list that will hold the names of the feature classes.  because the location field is not consistent across all the feature classes layerList
    #is actually a list of lists, where the first list, locationList, holds all the feature classes where the field name is LOCATION and the second
    #list, descriptionList, holds all the feature classes where the field name is LOCATIONDESCRIPTION.
    layerList = []
    locationList = []
    descriptionList = []

    if (DataType == "Feature Dataset"):
        #loop through the datasets in thisWorkspace to find the match
        datasets = arcpy.ListDatasets('', 'Feature')
        
        for fds in datasets:
            shortName = fds.split(".")[2]  ##the fullname of a feature class on sde includes the name of the database (PUBLICWORKS.publicworks.snCleanout") so the split method
            #allows us to access the actual feature class name

            if shortName == OriginalData:
                #once you have found the correct dataset you want to loop through the feature classes.  we then set three additional criteria: 1. it needs to be
                #a point feature class because lines can cross multiple parcels and their location is really based on the point structures they connect to;
                #2. it should not be part of the county-maintained sewer infrastructure (only valid for sanitary sewer); and 3. it should not be part of the abandoned
                #feature class, which is really a static dataset that should not be routinely updated aside from adding in new abandoned featues.
                for fc in arcpy.ListFeatureClasses('', '', fds):
                    if arcpy.Describe(fc).shapeType == "Point":
                        print fc
                        # ListFields(dataset, {wild_card}, {field_type})
                        newName = fc.split(".")[2]
                        if newName.endswith("COUNTY") == False and newName.startswith("Abnd") == False:
                            fields = arcpy.ListFields(fc)
                            #assuming it meets those criteria we want to loop through the field names and confirm that there is a location field associated with
                            #the feature class.  since there are two valid location fields, LOCATION and LOCATIONDESCRIPTION, and we will need to know the name of
                            #the location field later, we use if/elif to determine the correct field name and then create the feature layer only for those features
                            #where the value in that field is null. finally, the name of the feature class is appended into a list based on the field name.
                            for field in fields:
                                fieldName = str(field.name)
                                if fieldName == "LOCATION":
                                    FCLayer = arcpy.MakeFeatureLayer_management(thisWorkspace + "/" + fds + "/" + fc, newName + "Layer", fieldName + " IS NULL")
                                    result = arcpy.GetCount_management(FCLayer)
                                    print result
                                    locationList.append(newName)
                                    break
                                elif fieldName == "LOCATIONDESCRIPTION":
                                    FCLayer = arcpy.MakeFeatureLayer_management(thisWorkspace + "/" + fds + "/" + fc,
                                                                                newName + "Layer",
                                                                                fieldName + " IS NULL")
                                    result = arcpy.GetCount_management(FCLayer)
                                    print result
                                    descriptionList.append(newName)
                                    break
                #the locationList and descriptionList lists are then appended to the layerList list
                layerList.append(locationList)
                layerList.append(descriptionList)

                #the layerList is returned (making it accessible when you call the createLayers function)
                return layerList

    #if a single feature class is passed to the function, we use the ListDatasets and ListFeatureClasses to find it.
    elif (DataType == "Feature Class"):
        datasets = arcpy.ListDatasets('', 'Feature')
        # print datasets
        for fds in datasets:
        # print fds
            for fc in arcpy.ListFeatureClasses('', '', fds):
                print fc
                newName = fc.split(".")[2] #the full name of an SDE feature class includes the owner, so we use the split method to parse just the actual feature
                #class name and then compare that to the feature class name passed to the function.
                if newName == OriginalData:
                    print "Got it!"
                    if arcpy.Describe(fc).shapeType == "Point":  #only point feature classes can be used with this function since polygons and lines can cross
                        #multiple parcels.
                        print "it's a point!"
                        # ListFields(dataset, {wild_card}, {field_type})
                        fields = arcpy.ListFields(fc)  #find the correct location field, make a feature layer, and append the feature class to the correct list
                        for field in fields:
                            fieldName = str(field.name)
                            if fieldName == "LOCATION":
                                FCLayer = arcpy.MakeFeatureLayer_management(thisWorkspace + "/" + fds + "/" + fc, newName + "Layer", fieldName + " IS NULL")
                                result = arcpy.GetCount_management(FCLayer)
                                print result
                                locationList.append(newName)
                                break
                            elif fieldName == "LOCATIONDESCRIPTION":
                                FCLayer = arcpy.MakeFeatureLayer_management(thisWorkspace + "/" + fds + "/" + fc,
                                                                            newName + "Layer",
                                                                            fieldName + " IS NULL")
                                result = arcpy.GetCount_management(FCLayer)
                                print result
                                descriptionList.append(newName)
                                break
                            
                        #append the locationList and the descriptionList to the layerList and return the layerList
                        layerList.append(locationList)
                        layerList.append(descriptionList)
                        return layerList

    elif (DataType == "List"):   ##loop through feature dataset once and compare it to each item in the list
        print(OriginalData)
        checkCount = 0
        datasets = arcpy.ListDatasets('', 'Feature')
        for fds in datasets:
            print fds
            for fc in arcpy.ListFeatureClasses('', '', fds):
                # print fc
                newName = fc.split(".")[2]
                if newName in OriginalData:
                    print "Found It!"
                    fields = arcpy.ListFields(fc) #find the correct location field, make a feature layer, and append the feature class to the correct list
                    for field in fields:
                        fieldName = str(field.name)
                        if fieldName == "LOCATION":
                            FCLayer = arcpy.MakeFeatureLayer_management(thisWorkspace + "/" + fds + "/" + fc, newName + "Layer", fieldName + " IS NULL")
                            result = arcpy.GetCount_management(FCLayer)
                            print result
                            locationList.append(newName)
                            checkCount += 1
                            break
                        elif fieldName == "LOCATIONDESCRIPTION":
                            FCLayer = arcpy.MakeFeatureLayer_management(thisWorkspace + "/" + fds + "/" + fc,
                                                                        newName + "Layer",
                                                                        fieldName + " IS NULL")
                            result = arcpy.GetCount_management(FCLayer)
                            print result
                            descriptionList.append(newName)
                            checkCount += 1
                            break
                if checkCount >= len(OriginalData):
                    layerList.append(locationList)
                    layerList.append(descriptionList)
                    print layerList
                    return layerList
        if len(locationList) + len(descriptionList) < len(OriginalData):
            MissingData = []
            for item in OriginalData:
                if item not in locationList and item not in descriptionList:
                    MissingData.append(item)
                    print "ERROR: Feature classes were not found for following inputs " + str(MissingData)
            pass

    # Check to see if any layers were created.
    if len(locationList) == 0 and len(descriptionList) == 0:
        print "Error: No feature classes were found matching the provided inputs."
        quit()

    layerList.append(locationList)
    layerList.append(descriptionList)
    print layerList
    return layerList
        

'''In the function below we loop through the lists and use the spatial join to create an in-memory feature class, named joinWithin, between the layer and the parcel layer where the layer feature sits
within a parcel.  We use da.SearchCursor to iterate through joinWithin, extracting the parcelID, facilityID, and site address.  Using Select by Attributes we find any address points
with the same ParcelID.  If there is only one address point we calculate its site address into the layer's location field.  If there is more than one address point that matches 
we do a second in-memory join to find the address point that is nearest the selected feature and calculate
that site address into the location field.  If there is no address point we use the parcel site address for the location field.'''
def FeatureInParcel(layerList):
    # first make the address point layer
    print "Start the features in parcel function"
    AddressPoints = A1Connection + "/GIS_Data.A1.AddressFeatures/GIS_Data.A1.ActiveAddressPoints"
    arcpy.MakeFeatureLayer_management(AddressPoints, "AP_Layer")

    Parcels = A1Connection + "/GIS_Data.A1.TaxData/gis_data.A1.Parcels"

#layerlist is now a list of list, with the first list layerList[0] representing those feature classes where the field name is "LOCATION" and
    #layerList[1] includes feature classes where the field name is "LOCATIONDESCRIPTION".
    print layerList
    print len(layerList)
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

            result = arcpy.GetCount_management(joinWithin)
            print result

            if result > 0:
                # iterate through features that are within a parcel. "PARCEL_ID IS NOT NULL"
                with arcpy.da.SearchCursor(joinWithin, ["Parcel_ID", "FACILITYID", "SITE_ADDRE"]) as cursor:
                    for row in cursor:
                        print row
                        # select the address points with the same parcel ID
                        arcpy.SelectLayerByAttribute_management("AP_Layer", "NEW_SELECTION", "[PARCEl_ID] = " + str(row[0]))
                        # Select APs within the selected parcel
                        # PWLIB.transcribe(str(row[0]) + " Parcel contains " + str(
                        # arcpy.GetCount_management("AP_Layer")) + " Address Point(s)")
                        # If AP Count is 1, move the AP Address to the feature.
                        if int(arcpy.GetCount_management("AP_Layer")[0]) == 1:
                            print "There is one address point"
                            arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION",
                                                                    "[FACILITYID] = '" + str(row[1]) + "'")
                            layerResult = arcpy.GetCount_management(layer)
                            layerCount = int(layerResult.getOutput(0))
                            print layerCount

                            print "\tTransferring Address to layer " + str(row[1])
                            ap_cursor = arcpy.da.SearchCursor("AP_Layer", ["SITE_ADDRE"])
                            for AP in ap_cursor:
                                # PWLIB.transcribe("\t" + AP[0])
                                arcpy.CalculateField_management(layer, locationfield, "\"" + AP[0] + "\"", "", "")
                            del ap_cursor
                        # If AP Count is > 1,
                        # Create a spatial join using selected feature and selected address points, then choose the nearest one
                        elif int(arcpy.GetCount_management("AP_Layer")[0]) > 1:
                            print "There are multiple address points"
                            arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION",
                                                                    "[FACILITYID] = '" + str(row[1]) + "'")
                            layerResult = arcpy.GetCount_management(layer)
                            layerCount = int(layerResult.getOutput(0))
                            print layerCount

                            arcpy.SpatialJoin_analysis(layer, "AP_Layer", "in_memory/NearestAP", "JOIN_ONE_TO_ONE",
                                                       "KEEP_ALL", "", "CLOSEST")
                            arcpy.MakeFeatureLayer_management("in_memory/NearestAP", "NearestAP_Layer")
                            # PWLIB.transcribe("\tTransferring Address to swNode " + str(row[1]))
                            ap_cursor = arcpy.da.SearchCursor("NearestAP_Layer", ["SITE_ADDRE"])
                            for AP in ap_cursor:
                                # PWLIB.transcribe("\t" + AP[0])
                                arcpy.CalculateField_management(layer, locationfield, "\"" + AP[0] + "\"", "", "")
                            del ap_cursor
                        # If AP Count == 0, move the Parcel's Site Address to the feature
                        elif int(arcpy.GetCount_management("AP_Layer")[0]) == 0:
                            print "There are no address points"
                            print str(row[2])

                            arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION",
                                                                    "[FACILITYID] = '" + str(row[1]) + "'")
                            layerResult = arcpy.GetCount_management(layer)
                            layerCount = int(layerResult.getOutput(0))
                            arcpy.CalculateField_management(layer, locationfield, "\"" + str(row[2]) + "\"", "", "")
                            print layerCount
        i = i + 1
    FeatureNearParcel(layerList)

    return

'''This function below is run after the FeatureInParcel function and is used to calculate a location for those features that do not sit within a parcel.  The first step
is to do a new select by attribute query to select ONLY those features that still have a null value in the location field.  Next we do a spatial join with the parcel layer
to identify the closest parcel.  A search cursor is then used to iterate through the resulting in-memory feature class and the site adddress value is returned and used to
calculate the value of the individual feature.'''	
def FeatureNearParcel(layerList):
    print "Start the features outside of parcels function"
    # first make the address point layer
    AddressPoints = A1Connection + "/GIS_Data.A1.AddressFeatures/GIS_Data.A1.ActiveAddressPoints"
    arcpy.MakeFeatureLayer_management(AddressPoints, "AP_Layer")

    Parcels = A1Connection + "/GIS_Data.A1.TaxData/gis_data.A1.Parcels"

#layerlist is now a list of list, with the first list layerList[0] representing those feature classes where the field name is "LOCATION" and
    #layerList[1] includes feature classes where the field name is "LOCATIONDESCRIPTION".
    print layerList
    print len(layerList)
    i = 0
    for list in layerList:
        if i == 0:
            locationfield = "LOCATION"
        else:
            locationfield = "LOCATIONDESCRIPTION"

        for fc in layerList[i]:
            print locationfield
            layer = fc + "Layer"
            print layer
            joinClosest = "in_memory/joinClosest" + fc

            arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", "[" + locationfield + "] IS NULL")

            arcpy.SpatialJoin_analysis(layer, Parcels, joinClosest, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "", "CLOSEST", "",
                                       "")

            result = arcpy.GetCount_management(joinClosest)

            arcpy.AddJoin_management(layer, "OBJECTID", joinClosest, "TARGET_FID", "KEEP_ALL")

            if result > 0:
                arcpy.CalculateField_management(layer, locationfield, "[joinClosest" + fc + ".SITE_ADDRE]", "VB", )

                ##This is to check field names
                # fields = arcpy.ListFields(layer)
                # for field in fields:
                #     print field.name

            #     # iterate through features that are within a parcel. "PARCEL_ID IS NOT NULL" dont need a search cursor anylonger
            #     with arcpy.da.SearchCursor(joinClosest, ["Parcel_ID", "FACILITYID", "SITE_ADDRE"]) as cursor:
            #         for row in cursor:
            #             print row
            #             print str(row[2])
            #
            #             arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION",
            #                                                         "[FACILITYID] = '" + str(row[1]) + "'")
            #             layerResult = arcpy.GetCount_management(layer)
            #             layerCount = int(layerResult.getOutput(0))
            #             arcpy.CalculateField_management(layer, locationfield, "\"" + str(row[2]) + "\"", "", "")
            #             print layerCount
        print "Field Calculated"
        i = i + 1

    return


main()
