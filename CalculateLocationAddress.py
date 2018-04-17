

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
versionName = "FireHydrants" + todayhhmm
inWorkspace = "C:\Users\erikaki\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\PublicWorks_tax_sql_Erika.sde"
parentVersion = "Erikaki.UTILEDITS"

##WaterSystem = "Database Connections/A1_durham-gis.sde/gis_data.A1.WaterSystem" #feature dataset
Hydrants = "Database Connections/PublicWorks_tax_sql_Erika.sde/Publicworks.PUBLICWORKS.WaterSystem/Publicworks.PUBLICWORKS.wnHydrant"
FMZ = "Database Connections/A1_durham-gis.sde/GIS_Data.A1.E911_Layers/gis_data.A1.FMZ"
FireDistrict = "Database Connections/A1_durham-gis.sde/GIS_Data.A1.E911_Layers/gis_data.A1.Fire_District"
AddressPoints = "Database Connections/A1_durham-gis.sde/GIS_Data.A1.AddressFeatures/gis_data.A1.ActiveAddressPoints"

#If you want to use a Geodatabase comment this in, once I switched to version I did not need this.
# You can use this first inorder to create a copy of the Water System before editing. 

def MakeGDB():
    LogMessage ("***************************START***************************************")
    LogMessage(" Geodatabase creation...")
    FileGDBName="FireHydrants" + today
    OutputLocation= "H:/Work"
    arcpy.CreateFileGDB_management(OutputLocation, FileGDBName)
    # Set workspace
    arcpy.env.workspace="H:/Work/FireHydrants" + today + ".gdb"
    LogMessage ("Switched Workspace")
    thisWorkspace = arcpy.env.workspace
    LogMessage(" Geodatabase created")
##    LogMessage( FileGDBName + "/WaterSystem_CopyFeatures")
##    arcpy.Copy_management(WaterSystem, thisWorkspace + "/WaterSystem", "FeatureDataset")
##    LogMessage(" Water system copied.")
    
    LogMessage(" Copy Hydrant feature datasets...")
    arcpy.Copy_management(Hydrants, thisWorkspace+ "/Hydrants", "FeatureClass")
    LogMessage(" Hydrants copied.")

# You dont need to copy the FMZ/District because they are on A1. Not editing them but just hitting the data.     
##    LogMessage(" Copy FMZ feature datasets...")
##    arcpy.Copy_management(FMZ, thisWorkspace+ "/FMZ", "FeatureClass")
##    LogMessage(" FMZ copied.")
##
##    LogMessage(" Copy Fire Districts feature datasets...")
##    arcpy.Copy_management(FireDistrict, thisWorkspace+ "/FireDistrict", "FeatureClass")
##    LogMessage(" Fire Districts copied.")
    
    return    

def CreateVersion():

    LogMessage("******STARTING*******")

    # Create Version
    arcpy.CreateVersion_management(inWorkspace, parentVersion, versionName, "PROTECTED")
    LogMessage(" Version created.")
##    arcpy.env.workspace="C:/Work/FireZone" + today + ".gdb"

# Process: Make Feature Layer in order to run geoprocessing
    arcpy.MakeFeatureLayer_management(Hydrants, "HydrantLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(FMZ, "FMZLayer", "", "", "")
    arcpy.MakeFeatureLayer_management(FireDistrict, "FDLayer", "", "", "")
    LogMessage("Made Feature Layers ...")

# Switch to new version    
    LogMessage("Changing version to " + versionName + "...")
    arcpy.ChangeVersion_management("HydrantLayer", "TRANSACTIONAL", "ERIKAKI." + versionName, "")
   
    
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


def CalcAddress():
    LogMessage("Starting Address Calc")
##    SpatialJoin_analysis (target_features, join_features, out_feature_class, {join_operation}, {join_type}, {field_mapping}, {match_option}, {search_radius}, {distance_field_name})
##    target_features = "C:/TEMP/Utilities/Water.gdb/HydrantBU"
##    join_features = "Database Connections/A1_durham-gis.sde/GIS_Data.A1.AddressFeatures/gis_data.A1.ActiveAddressPoints"
    out_feature_class = "C:/TEMP/Utilities/Water.gdb/HydrantJoin"
    arcpy.MakeFeatureLayer_management(Hydrants, "HydrantLayer", "", "", "")
    
    arcpy.SpatialJoin_analysis("HydrantLayer", AddressPoints, out_feature_class, "JOIN_ONE_TO_ONE" , "KEEP_ALL","", "CLOSEST","","")
    LogMessage("Join Created")
    LogMessage("Join Data to Hydrants")
##    AddJoin_management (in_layer_or_view, in_field, join_table, join_field, {join_type})
##    arcpy.MakeFeatureLayer_management(target_features, "HydrantLayer", "", "", "")
    arcpy.AddJoin_management("HydrantLayer", "OBJECTID", out_feature_class, "TARGET_FID", "KEEP_ALL")
    LogMessage("Field Calculate over Site_Address to Location")


## Add Select All locations with NUll here


##CalculateField_management (in_table, field, expression, {expression_type}, {code_block})
    arcpy.CalculateField_management("HydrantLayer", "Publicworks.PUBLICWORKS.wnHydrant.LOCATIONDESCRIPTION", "[HydrantJoin.SITE_ADDRE]", "VB",)
    LogMessage("Nearest Addresses Calculated for Hydrants")


##It didnt do it on the version 0_0
    
def Cleanup():
    LogMessage("Switching back to parent version...")
    arcpy.ChangeVersion_management("HydrantLayer", "TRANSACTIONAL", parentVersion, "")

# Reconcile and post version.
    LogMessage("Reconciling/Posting version " + versionName)
    arcpy.ReconcileVersions_management(inWorkspace, "ALL_VERSIONS", parentVersion, "ERIKAKI." + versionName,  "LOCK_ACQUIRED", "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_EDIT_VERSION", "POST", "DELETE_VERSION")
    LogMessage( "Finished")

    
##MakeGDB()
CreateVersion()
##CalculateFMZ()
CalcAddress()
##Cleanup()

