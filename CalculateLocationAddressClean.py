

import arcpy, sys, string, os, time, shutil, tempfile

arcpy.env.overwriteOutput = True

today=time.strftime("%Y%m%d", time.localtime())
todayhhmm = time.strftime("%Y%m%dT%H%M", time.localtime())

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
soCasing =  "Database Connections/Publicworks_tax_sql_Erika.sde/Publicworks.PUBLICWORKS.SewerSystem/Publicworks.PUBLICWORKS.soCasing"
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

    LogMessage(FileGDBName + "/StormSystem_CopyFeatures")
    arcpy.Copy_management(StormSystem, thisWorkspace + "/StormSystem", "FeatureDataset")
    LogMessage(" Storm system copied.")


    return    

def CreateVersion():

    LogMessage("******STARTING*******")

    # Create Version
    arcpy.CreateVersion_management(inWorkspace, parentVersion, versionName, "PROTECTED")
    LogMessage(" Version created.")

# Process: Make Feature Layer in order to run geoprocessing
#     arcpy.MakeFeatureLayer_management(Hydrants, "HydrantLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(Manholes, "ManholeLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(ControlValve, "CValveLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(soCasing, "soCasingLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(AddressPoints, "APLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(Parcels, "ParcelsLayer", "", "", "")
    LogMessage("Made Feature Layers ...")

# Switch to new version
    LogMessage("Changing version to " + versionName + "...")
    arcpy.ChangeVersion_management("soCasingLayer", "TRANSACTIONAL", "ERIKAKI." + versionName, "")


def CalcAddressSub():
    LogMessage("Starting Address Calc")

    out_feature_class = "C:/Work/Address.gdb/JoinWithin"
    out_feature_class1 = "C:/Work/Address.gdb/JoinClosest"

    # arcpy.MakeFeatureLayer_management(feature,LayerName, "", "", "")
    LogMessage("Made Outputs")
    
    arcpy.SpatialJoin_analysis("soCasingLayer", Parcels, out_feature_class, "JOIN_ONE_TO_ONE" , "KEEP_ALL","", "COMPLETELY_WITHIN","","")
    LogMessage("Spatial Join Within Created")
    arcpy.SpatialJoin_analysis(out_feature_class, Parcels, out_feature_class1, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST","","")

    LogMessage("Spatial Join Closest Created")

    LogMessage("Start Join Data to Layer")
##    AddJoin_management (in_layer_or_view, in_field, join_table, join_field, {join_type})
    arcpy.AddJoin_management("soCasingLayer", "OBJECTID", out_feature_class1, "TARGET_FID", "KEEP_ALL")

##This isntworking
    arcpy.SelectLayerByAttribute_management("soCasingLayer", "NEW_SELECTION", "Publicworks.PUBLICWORKS.soCasing.LOCATIONDESCRIPTION IS NULL")

    result = arcpy.GetCount_management("soCasingLayer")
    LogMessage("There are %s records with NULL Location values..." % result)

    Cursor = arcpy.SearchCursor("soCasingLayer")

    for row in Cursor:
        LogMessage("Field Calculate over Site_Address to Location")
        ##CalculateField_management (in_table, field, expression, {expression_type}, {code_block})
        arcpy.CalculateField_management("soCasingLayer", "Publicworks.PUBLICWORKS.soCasing.LOCATIONDESCRIPTION","[JoinClosest.SITE_ADDRE_1]", "VB", )
        LogMessage("Nearest Addresses Calculated for Layer")

#     LogMessage("Field Calculate over Site_Address to Location")
#
#
# # Add AddressFromAP() Call here
#
#
# #CalculateField_management (in_table, field, expression, {expression_type}, {code_block})
#     arcpy.CalculateField_management(LayerName, "Publicworks.PUBLICWORKS.wnHydrant.LOCATIONDESCRIPTION","[HydrantJoin.SITE_ADDRE], "VB",)
#     arcpy.CalculateField_management("CValveLayer", "Publicworks.PUBLICWORKS.snControlValve.LOCATIONDESCRIPTION", "[CNValveClosest1.SITE_ADDRE_1]", "VB", )
#     LogMessage("Nearest Addresses Calculated for Layer")

def CalcAddressField():
    LogMessage("Start field calc")

    ##Must use field Name for Query not alias this doesnt work right now
    arcpy.SelectLayerByAttribute_management("soCasingLayer", "NEW_SELECTION", "LOCATIONDESCRIPTION IS NULL")

    result = arcpy.GetCount_management("soCasingLayer")
    LogMessage("There are %s records with NULL Location values..." % result)

    Cursor = arcpy.SearchCursor("soCasingLayer")

    for row in Cursor:
        LogMessage("Field Calculate over Site_Address to Location")
        ##CalculateField_management (in_table, field, expression, {expression_type}, {code_block})
        arcpy.CalculateField_management("soCasingLayer", "Publicworks.PUBLICWORKS.soCasing.LOCATIONDESCRIPTION","[JoinClosest1.SITE_ADDRE_1]", "VB", )
        LogMessage("Nearest Addresses Calculated for Layer")

##Miguels Code Portion
# def AddressFromAP():
#     # Create Layers. Nodes, Parcels, Joins, Address Points
#     arcpy.MakeFeatureLayer_management(Hydrants, "swNodes_Layer")
#     print "Stormwater Nodes Created."
#     fc = Directory + "/JoinFinal"
#     print "Joins Layer Created"
#     # JoinsCursor = arcpy.SearchCursor("Joins_Layer", "PARCEL_ID IS NOT NULL", fields="PARCEL_ID; PARCEL_ID_1; FACILITYID")
#     arcpy.MakeFeatureLayer_management("Database Connections/A1_durham-gis.sde/GIS_Data.A1.TaxData/GIS_Data.A1.Parcels",
#                                       "Parcels_Layer")
#     print "Parcels Layer Created."
#     arcpy.MakeFeatureLayer_management(
#         "Database Connections/A1_durham-gis.sde/GIS_Data.A1.AddressFeatures/GIS_Data.A1.ActiveAddressPoints",
#         "AP_Layer")
#
#     print "Addresspoints Layer Created."
#
#     # iterate through features that have a PID IS NOT NULL
#     with arcpy.da.SearchCursor(fc, ["Parcel_ID", "PARCEL_ID_1", "FACILITYID"],
#                                where_clause='PARCEL_ID IS NOT NULL') as cursor:
#         for row in cursor:
#             # select that parcel
#             arcpy.SelectLayerByAttribute_management("Parcels_Layer", "NEW_SELECTION", "[PARCEl_ID] = " + str(row[0]))
#             # Select APs within the selected parcel
#             arcpy.SelectLayerByLocation_management("AP_Layer", "WITHIN", "Parcels_Layer")
#             print str(row[0]) + " Parcel contains " + str(arcpy.GetCount_management("AP_Layer")) + " Address Point(s)"
#             # If AP Count is 1, move the AP Address to the feature.
#             # print type(arcpy.GetCount_management("AP_Layer"))
#             if int(arcpy.GetCount_management("AP_Layer")[0]) == 1:
#                 arcpy.SelectLayerByAttribute_management("swNodes_Layer", "NEW_SELECTION",
#                                                         "[FACILITYID] = " + str(row[2]))
#                 # calc/transfer the AP Address to the Feature
#                 print "\tTransferring Address to swNode " + str(row[2])
#                 APCursor = arcpy.da.SearchCursor("AP_Layer", ["SITE_ADDRE"])
#                 for AP in APCursor:
#                     print AP[0]
#                     """Currently having trouble effectively using the CalculateField tool to properly migrate the Address
#                     to the swNodes[LOCATION] field. My issue seems to hinge on the expression itself. Can Calucluate Field
#                     expression interact with the python script that it is being used in? Most of the examples I found online
#                     seemed to be self contained scripts within the greater program, kinda like glorified queries. """


def Cleanup(layer):
    LogMessage("Switching back to parent version...")
    arcpy.ChangeVersion_management(layer, "TRANSACTIONAL", parentVersion, "")

# Reconcile and post version.
    LogMessage("Reconciling/Posting version " + versionName)
    arcpy.ReconcileVersions_management(inWorkspace, "ALL_VERSIONS", parentVersion, "ERIKAKI." + versionName,  "LOCK_ACQUIRED", "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_EDIT_VERSION", "POST", "DELETE_VERSION")
    LogMessage( "Finished")


def GetCount():
    arcpy.SelectLayerByAttribute_management("soCasingLayer", "NEW_SELECTION", "LOCATIONDESCRIPTION IS NULL")
    result = arcpy.GetCount_management("soCasingLayer")
    LogMessage("There are %s records with NULL Location values..." % result)

# MakeGDB()
CreateVersion()
# CalcAddress(Hydrants, "HydrantLayer","Publicworks.PUBLICWORKS.wnHydrant.LOCATIONDESCRIPTION", "[HydrantJoin.SITE_ADDRE]")
CalcAddressSub()
# CalcAddressField()
# GetCount()
#Cleanup("soCasingLayer")
