

import arcpy, sys, string, os, time, shutil, tempfile

arcpy.env.overwriteOutput = True

today=time.strftime("%Y%m%d", time.localtime())
todayhhmm = time.strftime("%Y%m%dT%H%M", time.localtime())
Hydrants = "Database Connections/publiworks_TAX_SQL_Miguelto.sde/Publicworks.PUBLICWORKS.StormWater/Publicworks.PUBLICWORKS.swNodes"
Directory = "H:/Work/swNodes20180420.gdb"


def AddressFromAP():
    # Create Layers. Nodes, Parcels, Joins, Address Points
    arcpy.MakeFeatureLayer_management(Hydrants, "swNodes_Layer")
    print "Stormwater Nodes Created."
    fc = Directory+"/JoinFinal"
    print "Joins Layer Created"
    # JoinsCursor = arcpy.SearchCursor("Joins_Layer", "PARCEL_ID IS NOT NULL", fields="PARCEL_ID; PARCEL_ID_1; FACILITYID")
    arcpy.MakeFeatureLayer_management("Database Connections/A1_durham-gis.sde/GIS_Data.A1.TaxData/GIS_Data.A1.Parcels", "Parcels_Layer")
    print "Parcels Layer Created."
    arcpy.MakeFeatureLayer_management("Database Connections/A1_durham-gis.sde/GIS_Data.A1.AddressFeatures/GIS_Data.A1.ActiveAddressPoints","AP_Layer")

    print "Addresspoints Layer Created."

    # iterate through features that have a PID IS NOT NULL
    with arcpy.da.SearchCursor(fc, ["Parcel_ID", "PARCEL_ID_1", "FACILITYID"], where_clause= 'PARCEL_ID IS NOT NULL') as cursor:
        for row in cursor:
            # select that parcel
            arcpy.SelectLayerByAttribute_management("Parcels_Layer", "NEW_SELECTION", "[PARCEl_ID] = " + str(row[0]))
            # Select APs within the selected parcel
            arcpy.SelectLayerByLocation_management("AP_Layer", "WITHIN", "Parcels_Layer")
            print str(row[0]) + " Parcel contains " + str(arcpy.GetCount_management("AP_Layer")) + " Address Point(s)"
            # If AP Count is 1, move the AP Address to the feature.
            # print type(arcpy.GetCount_management("AP_Layer"))
            if int(arcpy.GetCount_management("AP_Layer")[0]) == 1:
                arcpy.SelectLayerByAttribute_management("swNodes_Layer", "NEW_SELECTION", "[FACILITYID] = " + str(row[2]))
                # calc/transfer the AP Address to the Feature
                print "\tTransferring Address to swNode " + str(row[2])
                APCursor = arcpy.da.SearchCursor("AP_Layer", ["SITE_ADDRE"])
                for AP in APCursor:
                    print AP[0]
                    """Currently having trouble effectively using the CalculateField tool to properly migrate the Address
                    to the swNodes[LOCATION] field. My issue seems to hinge on the expression itself. Can Calucluate Field
                    expression interact with the python script that it is being used in? Most of the examples I found online
                    seemed to be self contained scripts within the greater program, kinda like glorified queries. """
#   //if AP count is > 1
#       //select AP nearest to feature from selected AP
#       //calc/transfer the AP Address to the feature
#   //else
#       //calc/transfer the associated parcel address from the ParcelNearestFeature FC


def LogMessage( message):
    print time.strftime ("%Y-%m-%dT%H:%M:%S ", time.localtime()) + message
    return

# Set workspace
arcpy.Workspace="H:/Work"


# Global variables: (Created this to work within a version not .gdb)
versionName = "LocationCalc" + todayhhmm
inWorkspace = "C:\Users\erikaeno\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\PublicWorks_tax_sql_Erika.sde"
parentVersion = "Erikaki.UTILEDITS_EE"

##Datasets
WaterSystem = "Database Connections/A1_durham-gis.sde/gis_data.A1.WaterSystem" #feature dataset
SewerSystem = "Database Connections/A1_durham-gis.sde/gis_data.A1.SewerSystem" #feature dataset

##Feature Classes
Hydrants = "Database Connections/PublicWorks_tax_sql_Erika.sde/Publicworks.PUBLICWORKS.WaterSystem/Publicworks.PUBLICWORKS.wnHydrant"
Manholes = "Database Connections/Publicworks_tax_sql_Erika.sde/Publicworks.PUBLICWORKS.SewerSystem/Publicworks.PUBLICWORKS.snManhole"
ControlValve = "Database Connections/Publicworks_tax_sql_Erika.sde/Publicworks.PUBLICWORKS.SewerSystem/Publicworks.PUBLICWORKS.snControlValve"

AddressPoints = "Database Connections/A1_durham-gis.sde/GIS_Data.A1.AddressFeatures/gis_data.A1.ActiveAddressPoints"
Parcels = "Database Connections/A1_durham-gis.sde/GIS_Data.A1.TaxData/gis_data.A1.Parcels"

#If you want to use a Geodatabase comment this in, once I switched to version I did not need this.
# You can use this first inorder to create a copy of the Water System before editing. 

def MakeGDB():
    LogMessage ("***************************START***************************************")
    LogMessage(" Geodatabase creation...")
    FileGDBName="SystemBU" + today
    OutputLocation= "C:/Work"
    arcpy.CreateFileGDB_management(OutputLocation, FileGDBName)
    # Set workspace
    arcpy.env.workspace="C:/Work/SystemBU" + today + ".gdb"
    LogMessage ("Switched Workspace")
    thisWorkspace = arcpy.env.workspace
    LogMessage(" Geodatabase created")
    #
    # LogMessage( FileGDBName + "/WaterSystem_CopyFeatures")
    # arcpy.Copy_management(WaterSystem, thisWorkspace + "/WaterSystem", "FeatureDataset")
    # LogMessage(" Water system copied.")

    LogMessage(FileGDBName + "/SewerSystem_CopyFeatures")
    arcpy.Copy_management(SewerSystem, thisWorkspace + "/SewerSystem", "FeatureDataset")
    LogMessage(" Sewer system copied.")

    # LogMessage(" Copy Hydrant feature datasets...")
    # arcpy.Copy_management(Hydrants, thisWorkspace+ "/Hydrants", "FeatureClass")
    # LogMessage(" Hydrants copied.")

    return    

def CreateVersion():

    LogMessage("******STARTING*******")

    # Create Version
    arcpy.CreateVersion_management(inWorkspace, parentVersion, versionName, "PROTECTED")
    LogMessage(" Version created.")

# Process: Make Feature Layer in order to run geoprocessing
#     arcpy.MakeFeatureLayer_management(Hydrants, "HydrantLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(Manholes, "ManholeLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(ControlValve, "CNValveLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(AddressPoints, "APLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(Parcels, "ParcelsLayer", "", "", "")
    LogMessage("Made Feature Layers ...")

# Switch to new version
    LogMessage("Changing version to " + versionName + "...")
    arcpy.ChangeVersion_management("CNValveLayer", "TRANSACTIONAL", "ERIKAKI." + versionName, "")



# def CalcAddress(feature, LayerName, LayerField, JoinField):
#     LogMessage("Starting Address Calc")
#     ##    SpatialJoin_analysis (target_features, join_features, out_feature_class, {join_operation}, {join_type}, {field_mapping}, {match_option}, {search_radius}, {distance_field_name})
#
# out_feature_class = "H:/Work/SystemBU" + today + ".gdb/ClosestJoin"
# arcpy.MakeFeatureLayer_management(feature, LayerName, "", "", "")
#
# arcpy.SpatialJoin_analysis(LayerName, Parcels, out_feature_class, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "COMPLETELY_WITHIN","", "")
#     LogMessage("Spatial Join Within Created")
#
# arcpy.SpatialJoin_analysis(LayerName, Parcels, out_feature_class, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST","", "")
#
# LogMessage("Join Closest Created")

# LogMessage("Join Data to Layer")
# ##    AddJoin_management (in_layer_or_view, in_field, join_table, join_field, {join_type})
# ##    arcpy.MakeFeatureLayer_management(target_features, "HydrantLayer", "", "", "")
# arcpy.AddJoin_management(LayerName, "OBJECTID", out_feature_class, "TARGET_FID", "KEEP_ALL")
# LogMessage("Field Calculate over Site_Address to Location")
#
#

# def CalcAddressSub(feature,LayerName,LayerField, JoinField):

# def CalcAddressSub(LayerField, JoinField):
def CalcAddressSub():
    LogMessage("Starting Address Calc")
##    SpatialJoin_analysis (target_features, join_features, out_feature_class, {join_operation}, {join_type}, {field_mapping}, {match_option}, {search_radius}, {distance_field_name})

    out_feature_class = "C:/Work/Address.gdb/CNValveWithin1"
    out_feature_class1 = "C:/Work/Address.gdb/CNValveClosest1"

    # arcpy.MakeFeatureLayer_management(feature,LayerName, "", "", "")
    
    arcpy.SpatialJoin_analysis("CNValveLayer", Parcels, out_feature_class, "JOIN_ONE_TO_ONE" , "KEEP_ALL","", "COMPLETELY_WITHIN","","")
    LogMessage("Spatial Join Within Created")
    arcpy.SpatialJoin_analysis(out_feature_class, Parcels, out_feature_class1, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST","","")

    LogMessage("Spatial Join Closest Created")

    LogMessage("Start Join Data to Layer")
##    AddJoin_management (in_layer_or_view, in_field, join_table, join_field, {join_type})
##    arcpy.MakeFeatureLayer_management(target_features, "HydrantLayer", "", "", "")
    arcpy.AddJoin_management("CNValveLayer", "OBJECTID", out_feature_class1, "TARGET_FID", "KEEP_ALL")
    # LogMessage("Field Calculate over Site_Address to Location")


## Add AddressFromAP() Call here


##CalculateField_management (in_table, field, expression, {expression_type}, {code_block})
    # arcpy.CalculateField_management(LayerName, "Publicworks.PUBLICWORKS.wnHydrant.LOCATIONDESCRIPTION","[HydrantJoin.SITE_ADDRE], "VB",)
    # arcpy.CalculateField_management("ManholeLayer", LayerField, JoinField, "VB",)
    # LogMessage("Nearest Addresses Calculated for Layer")

def CalcAddress():

    # Must use field Name for Query not alias this doesnt work right now
    # arcpy.SelectLayerByAttribute_management("ManholeLayer", "NEW_SELECTION", "LOCATIONDESCRIPTION IS NULL")
    #
    # result = arcpy.GetCount_management("ManholeLayer")
    # LogMessage("There are %s records with NULL Location values..." % result)

    Cursor = arcpy.SearchCursor("CNValveLayer")

    for row in Cursor:
        LogMessage("Field Calculate over Site_Address to Location")
        # Must use field Name for Query not alias this doesnt work right now i bet you cant use this in a search coursor
        # arcpy.SelectLayerByAttribute_management("ManholeLayer", "NEW_SELECTION", "LOCATIONDESCRIPTION IS NULL")
        #
        # result = arcpy.GetCount_management("ManholeLayer")
        # LogMessage("There are %s records with NULL Location values..." % result)

        ##CalculateField_management (in_table, field, expression, {expression_type}, {code_block})
        arcpy.CalculateField_management("CNValveLayer", "Publicworks.PUBLICWORKS.snControlValve.LOCATIONDESCRIPTION","[CNValveClosest1.SITE_ADDRE_1]", "VB", )
        LogMessage("Nearest Addresses Calculated for Layer")


def AddressInParcel(feature_class, final_join):
    """ ARGS
        feature_class : The point feature class that is being updated.
        final_join :    The dialog path to the join that has the feature class being updated.
                        Final Join is expected to be joined as follows;
                        Feature class joined to parcels containing the feature.
                        The result being joined to parcels nearest the feature.

        ASSUMPTIONS     - The name of the field being updated is "LOCATION"

        Takes a Feature Class and updates the location field and updates
        it with the site address of the Address Point contained within the same parcel.
        If there is more than one Address Point, it will take the nearest address point to the feature.
        If there are no Address Points, it will take the site address sof the parcel."""
    # Create Layers; Features, Parcels, Joins, Address Points
    feature_class = "Database Connections/publiworks_TAX_SQL_Miguelto.sde/Publicworks.PUBLICWORKS.swNodes"
    arcpy.MakeFeatureLayer_management(feature_class, "Feature_Layer")
    print "Feature Layer Created."
    final_join = "H:/Work/swNodes20180420.gdb/JoinFinal"
    print "Joins Table Selected."
    arcpy.MakeFeatureLayer_management("Database Connections/A1_durham-gis.sde/GIS_Data.A1.TaxData/GIS_Data.A1.Parcels",
                                      "Parcels_Layer")
    print "Parcels Layer Created."
    arcpy.MakeFeatureLayer_management(
        "Database Connections/A1_durham-gis.sde/GIS_Data.A1.AddressFeatures/GIS_Data.A1.ActiveAddressPoints",
        "AP_Layer")
    print "Address Points Layer Created."
    # iterate through features that are within a parcel. "PARCEL_ID IS NOT NULL"
    with arcpy.da.SearchCursor(final_join, ["Parcel_ID", "PARCEL_ID_1", "FACILITYID"],
                               where_clause='PARCEL_ID IS NOT NULL') as cursor:
        for row in cursor:
            # select that parcel
            arcpy.SelectLayerByAttribute_management("Parcels_Layer", "NEW_SELECTION", "[PARCEl_ID] = " + str(row[0]))
            # Select APs within the selected parcel
            arcpy.SelectLayerByLocation_management("AP_Layer", "WITHIN", "Parcels_Layer")
            print str(row[0]) + " Parcel contains " + str(arcpy.GetCount_management("AP_Layer")) + " Address Point(s)"
            # If AP Count is 1, move the AP Address to the feature.
            if int(arcpy.GetCount_management("AP_Layer")[0]) == 1:
                arcpy.SelectLayerByAttribute_management("Feature_Layer", "NEW_SELECTION",
                                                        "[FACILITYID] = '" + str(row[2]) + "'")
                print "\tTransferring Address to swNode " + str(row[2])
                ap_cursor = arcpy.da.SearchCursor("AP_Layer", ["SITE_ADDRE"])
                for AP in ap_cursor:
                    print "\t" + AP[0]
                    arcpy.CalculateField_management("Feature_Layer", "LOCATION", "\"" + AP[0] + "\"", "", "")
                del ap_cursor
            elif int(arcpy.GetCount_management("AP_Layer")[0]) > 1:
                # Create a spatial join using selected feature and selected address points, then choose the nearest one
                arcpy.SpatialJoin_analysis("Feature_Layer", "AP_Layer", "in_memory/NearestAP", "JOIN_ONE_TO_ONE",
                                           "KEEP_ALL", "", "CLOSEST")
                arcpy.MakeFeatureLayer_management("in_memory/NearestAP", "NearestAP_Layer")
                print "\tTransferring Address to swNode " + str(row[2])
                ap_cursor = arcpy.da.SearchCursor("NearestAP_Layer", ["SITE_ADDRE"])
                for AP in ap_cursor:
                    print "\t" + AP[0]
                    arcpy.CalculateField_management("Feature_Layer", "LOCATION", "\"" + AP[0]+ "\"", "", "")
                del ap_cursor
            elif int(arcpy.GetCount_management("AP_Layer")[0]) == 0:
                arcpy.SelectLayerByAttribute_management("Feature_Layer", "NEW_SELECTION",
                                                        "[FACILITYID] = '" + str(row[2]) + "'")
                parcel_cursor = arcpy.da.SearchCursor("Parcel_Layer", ["SITE_ADDRE"])
                for parcel in parcel_cursor:
                    print "\t" + parcel[0]
                    arcpy.CalculateField_management("Feature_Layer", "LOCATION", "\"" + parcel[0] + "\"", "", "")
                del parcel_cursor


def Cleanup(layer):
    LogMessage("Switching back to parent version...")
    arcpy.ChangeVersion_management(layer, "TRANSACTIONAL", parentVersion, "")

# Reconcile and post version.
    LogMessage("Reconciling/Posting version " + versionName)
    arcpy.ReconcileVersions_management(inWorkspace, "ALL_VERSIONS", parentVersion, "ERIKAKI." + versionName,  "LOCK_ACQUIRED", "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_EDIT_VERSION", "POST", "DELETE_VERSION")
    LogMessage( "Finished")


# MakeGDB()
CreateVersion()
# CalcAddress(Hydrants, "HydrantLayer","Publicworks.PUBLICWORKS.wnHydrant.LOCATIONDESCRIPTION", "[HydrantJoin.SITE_ADDRE]")
# def CalcAddressSub(feature,LayerName,LayerField, JoinField):
# CalcAddressSub("Publicworks.PUBLICWORKS.snManhole.LOCATIONDESCRIPTION","[ManholesClosest.SITE_ADDRE_1]")
CalcAddressSub()
CalcAddress()

##Cleanup("ManholeLayer")

