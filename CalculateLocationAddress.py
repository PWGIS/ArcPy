

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
inWorkspace = "C:\Users\erikaki\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\PublicWorks_tax_sql_Erika.sde"
parentVersion = "Erikaki.UTILEDITS"

##Datasets
WaterSystem = "Database Connections/A1_durham-gis.sde/gis_data.A1.WaterSystem" #feature dataset
SewerSystem = "Database Connections/A1_durham-gis.sde/gis_data.A1.SewerSystem" #feature dataset

##Feature Classes
Hydrants = "Database Connections/PublicWorks_tax_sql_Erika.sde/Publicworks.PUBLICWORKS.WaterSystem/Publicworks.PUBLICWORKS.wnHydrant"
Manhole = "Database Connections/Publicworks_tax_sql_Erika.sde/Publicworks.PUBLICWORKS.SewerSystem/Publicworks.PUBLICWORKS.snManhole"

AddressPoints = "Database Connections/A1_durham-gis.sde/GIS_Data.A1.AddressFeatures/gis_data.A1.ActiveAddressPoints"
Parcels = "Database Connections/A1_durham-gis.sde/GIS_Data.A1.TaxData/gis_data.A1.Parcels"

#If you want to use a Geodatabase comment this in, once I switched to version I did not need this.
# You can use this first inorder to create a copy of the Water System before editing. 

def MakeGDB():
    LogMessage ("***************************START***************************************")
    LogMessage(" Geodatabase creation...")
    FileGDBName="SystemBU" + today
    OutputLocation= "H:/Work"
    arcpy.CreateFileGDB_management(OutputLocation, FileGDBName)
    # Set workspace
    arcpy.env.workspace="H:/Work/SystemBU" + today + ".gdb"
    LogMessage ("Switched Workspace")
    thisWorkspace = arcpy.env.workspace
    LogMessage(" Geodatabase created")

    LogMessage( FileGDBName + "/WaterSystem_CopyFeatures")
    arcpy.Copy_management(WaterSystem, thisWorkspace + "/WaterSystem", "FeatureDataset")
    LogMessage(" Water system copied.")

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
    arcpy.MakeFeatureLayer_management(Hydrants, "HydrantLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(Manhole, "ManholeLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(AddressPoints, "APLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(Parcels, "ParcelsLayer", "", "", "")
    LogMessage("Made Feature Layers ...")

# Switch to new version    
    LogMessage("Changing version to " + versionName + "...")
    arcpy.ChangeVersion_management("ManholeLayer", "TRANSACTIONAL", "ERIKAKI." + versionName, "")
   
    
# Select by Location, and Calculate Field
def CalculateFMZ():
    LogMessage("Calculate Fire Maintance Zones") 
# Process: Select Layer By Location

    Districts = ['01', '02', '03', '04', '05','06', '07', '08', '09', '10',
                  '11', '12', '13', '14', '15', '16', '81', '82', '83', '84', '85','BAH1', 'BAH2', 'BAH3',
                  'CH2', 'CH3', 'ENO', 'LEB1', 'MRI1', 'NEW',
                 'RAL', 'RED1']

    for District in Districts:

        query = "CAD = "+ "'" + District + "'" + " AND " + "COUNTY = "+ "'DURHAM'"

        print 'query :' + query

        fieldname = "'" + District + "'"
        
        print 'fieldname :' + fieldname

        arcpy.SelectLayerByAttribute_management ("FDLayer", "NEW_SELECTION", query)
        
        print 'district selected'

        arcpy.SelectLayerByLocation_management ("HydrantLayer", "WITHIN","FDLayer", "", "NEW_SELECTION")
        
        print 'select by location complete'

        arcpy.CalculateField_management ("HydrantLayer", "DISTRICT", "\"" + District + "\"", "", "")
        
        print 'District field populated'
        
    print "Districts calculated!"

    rows = arcpy.SearchCursor ("FMZLayer")

    for row in rows:

        query = "Zone = "+ "'" + row.ZONE + "'"

        arcpy.SelectLayerByAttribute_management ("FMZLayer","NEW_SELECTION",query)

        print 'FMZ selected'

        arcpy.SelectLayerByLocation_management ("HydrantLayer", "WITHIN","FMZLayer", "", "NEW_SELECTION")

        print 'Select by location complete.'

        arcpy.CalculateField_management ("HydrantLayer", "ZONE_", "\"" + row.ZONE + "\"", "", "")

        print 'Zone field populated.'

        print "Zones calculated!"


def CalcAddress(feature, LayerName, LayerField, JoinField):
    LogMessage("Starting Address Calc")
##    SpatialJoin_analysis (target_features, join_features, out_feature_class, {join_operation}, {join_type}, {field_mapping}, {match_option}, {search_radius}, {distance_field_name})
##    target_features = "C:/TEMP/Utilities/Water.gdb/HydrantBU"
##    join_features = "Database Connections/A1_durham-gis.sde/GIS_Data.A1.AddressFeatures/gis_data.A1.ActiveAddressPoints"

    # out_feature_class = "H:/Work/SystemBU" + today + ".gdb/Join"

    out_feature_class = "H:/Work/SystemBU" + today + ".gdb/ClosestJoin"
    arcpy.MakeFeatureLayer_management(feature,LayerName, "", "", "")
    
    arcpy.SpatialJoin_analysis(LayerName, AddressPoints, out_feature_class, "JOIN_ONE_TO_ONE" , "KEEP_ALL","", "CLOSEST","","")
    LogMessage("Join Created")
    LogMessage("Join Data to Layer")
##    AddJoin_management (in_layer_or_view, in_field, join_table, join_field, {join_type})
##    arcpy.MakeFeatureLayer_management(target_features, "HydrantLayer", "", "", "")
    arcpy.AddJoin_management(LayerName, "OBJECTID", out_feature_class, "TARGET_FID", "KEEP_ALL")
    LogMessage("Field Calculate over Site_Address to Location")


## Add Select All locations with NUll here


##CalculateField_management (in_table, field, expression, {expression_type}, {code_block})
    arcpy.CalculateField_management(LayerName, LayerField, JoinField, "VB",)
    LogMessage("Nearest Addresses Calculated for Layer")


##It didnt do it on the version 0_0
    
def Cleanup(layer):
    LogMessage("Switching back to parent version...")
    arcpy.ChangeVersion_management(layer, "TRANSACTIONAL", parentVersion, "")

# Reconcile and post version.
    LogMessage("Reconciling/Posting version " + versionName)
    arcpy.ReconcileVersions_management(inWorkspace, "ALL_VERSIONS", parentVersion, "ERIKAKI." + versionName,  "LOCK_ACQUIRED", "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_EDIT_VERSION", "POST", "DELETE_VERSION")
    LogMessage( "Finished")

    
MakeGDB()
CreateVersion()
##CalculateFMZ()
CalcAddress(Hydrants, "HydrantLayer","Publicworks.PUBLICWORKS.wnHydrant.LOCATIONDESCRIPTION", "[HydrantJoin.SITE_ADDRE]")
##Cleanup("ManholeLayer")

