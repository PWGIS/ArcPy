

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
StormSystem = "Database Connections/A1_durham-gis.sde/gis_data.A1.StormWater" #feature dataset

##Feature Classes
Hydrants = "Database Connections/PublicWorks_tax_sql_Erika.sde/Publicworks.PUBLICWORKS.WaterSystem/Publicworks.PUBLICWORKS.wnHydrant"
Manholes = "Database Connections/Publicworks_tax_sql_Erika.sde/Publicworks.PUBLICWORKS.SewerSystem/Publicworks.PUBLICWORKS.snManhole"
ControlValve = "Database Connections/Publicworks_tax_sql_Erika.sde/Publicworks.PUBLICWORKS.SewerSystem/Publicworks.PUBLICWORKS.snControlValve"
soCasing =  "Database Connections/Publicworks_tax_sql_Erika.sde/Publicworks.PUBLICWORKS.SewerSystem/Publicworks.PUBLICWORKS.soCasing"
AddressPoints = "Database Connections/A1_durham-gis.sde/GIS_Data.A1.AddressFeatures/gis_data.A1.ActiveAddressPoints"
Parcels = "Database Connections/A1_durham-gis.sde/GIS_Data.A1.TaxData/gis_data.A1.Parcels"

#If you want to use a Geodatabase comment this in, once I switched to version I did not need this.
# You can use this first in order to create a copy of the Utility Systems before editing.

def MakeGDB():
    LogMessage ("***************************STARTING************************************")
    LogMessage(" Geodatabase creation...")
    FileGDBName="SystemBU" + today
    OutputLocation= "C:/Work"
    arcpy.CreateFileGDB_management(OutputLocation, FileGDBName)
    # Set workspace as the gdb you just created.
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


def CreateJoins():
    LogMessage("Starting Join Creations")

## This is the locations of the output join tables that will be referenced later (** Should Update to be the new gdb created earlier. Because if a join already exisits inside with the same name it will error out**)
    out_feature_class = "C:/Work/Address.gdb/JoinWithin"
    out_feature_class1 = "C:/Work/Address.gdb/JoinClosest"
    LogMessage("Made Join Outputs")

## Create Spatial Join Layer to Parcels: Features that are completely within

    # arcpy.SpatialJoin_analysis("soCasingLayer", Parcels, out_feature_class, "JOIN_ONE_TO_ONE" , "KEEP_ALL","", "COMPLETELY_WITHIN","","")
    # LogMessage("Spatial Join Within Created")

    ## Need to add code exit hwere if no features are within parcel to keep going to next line

## Create Spatial Join Layer to Parcels: Features that are closest (THIS IS WERE WE NEED TO INTEGRATE THE ADDRESS POINT CODE)

    arcpy.SpatialJoin_analysis("soCasingLayer", Parcels, out_feature_class1, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST","","")
    LogMessage("Spatial Join Closest Created")

    LogMessage("Start Join Data to Layer")
## Joins the layer you want to update with the closest output join. ** We need to move this to the completly within part and then calc completely within then do the ones that are closest using miguels code.

## AddJoin_management (in_layer_or_view, in_field, join_table, join_field, {join_type})
    arcpy.AddJoin_management("soCasingLayer", "OBJECTID", out_feature_class1, "TARGET_FID", "KEEP_ALL")

## Selects all the records with NULL Location Fields

    arcpy.SelectLayerByAttribute_management("soCasingLayer", "NEW_SELECTION", "Publicworks.PUBLICWORKS.soCasing.LOCATIONDESCRIPTION IS NULL")

    result = arcpy.GetCount_management("soCasingLayer")
    LogMessage("There are %s records with NULL Location values..." % result)

    Cursor = arcpy.SearchCursor("soCasingLayer")
    LogMessage("Field Calculate over Site_Address to Location")

    for row in Cursor:

        ##CalculateField_management (in_table, field, expression, {expression_type}, {code_block})
        arcpy.CalculateField_management("soCasingLayer", "Publicworks.PUBLICWORKS.soCasing.LOCATIONDESCRIPTION","[JoinClosest.SITE_ADDRE]", "VB", )

    LogMessage("Field Site_Address Calculated over to Location")

## Add AddressInParcel() Call here


def AddressInParcel(feature_class, final_join):
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


def transcribe(message, dir_location = os.path.dirname(__file__)+ "/"):
    """ ARGS:
    message: a string variable to be written to the file and console
    dir_location: the location of the directory to write the file to, assumes '/' notation
        default location is the same directory that the program is being run from.

    DESCRIPTION:
    Function writes the STRING argument out to a text file.
    The string is also written to the console.
    The file name is the name of the program plus the date that it is run.
    The file is written to the H:/Work directory.
    The contents include timestamped records of each string as it is provided.

    DEPENDENCIES:
    Utilizes the LogMessage function to write to console.

    Assumptions:
    There must be an H: directory.
    """
    # Append message to file, create file if it does not exist
    # File location is in the same directory the program is being run from
    # File Name is 'ProgramName' + Date, e.g., foobar_2018-01-30
    txt_file = open(dir_location + os.path.basename(__file__).replace(".py",
                    "_" + time.strftime("%Y-%m-%d",time.localtime()) + ".txt"), "a")
    txt_file.write(time.strftime("%H:%M", time.localtime()) + "\t" + message + "\n")
    LogMessage(message)
    txt_file.close()


# MakeGDB()
CreateVersion()
CreateJoins()
#Cleanup("soCasingLayer")

