import arcpy
import sys, string, os, time, shutil, tempfile, logging, datetime

arcpy.env.overwriteOutput = True

today=time.strftime("%Y%m%d", time.localtime())
todayhhmm = time.strftime("%Y%m%dT%H%M", time.localtime())
currentDate = datetime.date.today()
lastWeek = currentDate - datetime.timedelta(days=7)
sevenDays = lastWeek.strftime("%Y%m%d")
LWP = ''


def test():
    print today
    print currentDate
    print lastWeek
    print sevenDays
    print lastWeeksParcel
def LogMessage (message):
    print time.strftime ("%Y-%m-%dT%H:%M:%S ", time.localtime()) + message
    return

# Global Variables
A1_Parcels = "Database Connections/gis_data_A1.sde/GIS_Data.A1.TaxData/gis_data.A1.Parcels"
Outputlocation = "C:\Work\ParcelBackup"
lastWeeksParcel = "C:\Work\ParcelBackup\ParcelBackup" + sevenDays + ".gdb\Parcels"
# Set Workspace
arcpy.Workspace = "C:\Work\ParcelBackup\ParcelBackup" + today + ".gdb"
#create variable for last week's parcel backup referencing sevenDays variable
thisWorkspace = arcpy.Workspace
inWorkspace = "C:\Work\ParcelBackup\PW_OWNER.sde"
PWParcelChanges = "C:\Work\ParcelBackup\PW_OWNER.sde\PW.PW.ParcelChanges\PW.PW.ParcelChanges"

def MakeGDB():
    LogMessage(" Geodatabase Creation...")
    FileGDBName = "ParcelBackup" + today
    arcpy.CreateFileGDB_management(Outputlocation, FileGDBName)
    LogMessage("Geodatabase Created")
    return

def CopyFeatures():
    LogMessage (" Copy A1 Parcels Feature")
    # Copy Parcels from A1
    arcpy.Copy_management (A1_Parcels, thisWorkspace + "\Parcels")
    LogMessage (" Copy is complete")
    # Make FeatureLayer of A1 Parcels

    return

def MakeFeatureLayer():
    # Make FeatureLayer of Backup Parcels
    LogMessage (" Make Feature Layer of the last backup parcels")
    #You need to figure out how to dynamically set prior week's geodatabase name.  YOu will have to use function Now()
    arcpy.MakeFeatureLayer_management(lastWeeksParcel, "parcelbackup_lyr")
    LogMessage (" Make Feature Layer of A1 Parcels")
    arcpy.MakeFeatureLayer_management(thisWorkspace + "\Parcels", "A1_Parcel_lyr")
    return

def SelectByLocation():
    # Select Parcel backup that are identical to A1 Parcels
    LogMessage (" Select Parcels that are equal to A1_Parcels")
    #arcpy.SelectLayerByLocation_management("A1_Parcel_lyr", "are_identical_to", "parcelbackup_lyr")
    arcpy.SelectLayerByLocation_management("parcelbackup_lyr", "are_identical_to", "A1_Parcel_lyr")

def ReverseSelection():
    # Select the Parcels that have changed since the last backup
    LogMessage (" Reverse Selection")
    #arcpy.SelectLayerByLocation_management("A1_Parcel_lyr", None, None, "", "SWITCH_SELECTION")
    arcpy.SelectLayerByLocation_management("parcelbackup_lyr", None, None, "", "SWITCH_SELECTION")

def CreateNewFeatureclass():
    # Get a count of all of the parcels that have changed and create a new featureclass of the changed parcels if there are any
    LogMessage (" Create New Featureclass of Parcel Changes")
    matchcount = int(arcpy.GetCount_management("parcelbackup_lyr").getOutput(0))
    #LogMessage (matchcount)
    if matchcount == 0:
        print (" There are no parcel changes")
        exit()
    else:
        arcpy.CopyFeatures_management("parcelbackup_lyr", "C:\Work\ParcelBackup\ParcelChanges.gdb\ParcelChanges" + today)
        #print (matchcount + " parcel changes".format (matchcount))
        print matchcount

def DeleteFields():
    LogMessage("Delete fields.")
    arcpy.DeleteField_management("C:\Work\ParcelBackup\ParcelChanges.gdb\ParcelChanges" + today, ["PIN", "FRONT_DIM", "POLY_ACRE", \
                                 "SUM_ACRE", "OLD_ID", "USERINT", "CITY_CODE", \
                                 "ACCT_", "OWADR2", "OWADR3", "Parcels_OWADR4", \
                                 "OWCITY", "Parcels_OWSTA", "OWZIPA", "DIST_CODE", \
                                 "SplitTaxDis", "SplitTaxDec", "LAND_USE", "LANDUSE_DESC", \
                                 "NBR_CLASS", "NBR_CODE", "EXEMPT_CODE", "LAND_VALUE", \
                                 "BLDG_VALUE", "TOTAL_VALU", "DEED_BOOK", "DEED_PAGE", \
                                 "PLAT_BOOK", "PLAT_PAGE", "DATE_SOLD", "SALE_PRICE", \
                                 "SUBD_ID", "SUBD_DESC", "CLASS_CODE"])
    LogMessage(" Fields deleted.")

def AddField():
    LogMessage("Add field.")
    arcpy.AddField_management("C:\Work\ParcelBackup\ParcelChanges.gdb\ParcelChanges" + today, "CreateDate", "DATE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    LogMessage(" Field added.")
    arcpy.CalculateField_management("C:\Work\ParcelBackup\ParcelChanges.gdb\ParcelChanges" + today, "CreateDate", "datetime.datetime.now( )", "PYTHON", "")
    LogMessage(" Field Calculated.")
    arcpy.env.workspace = "C:\Work\ParcelBackup\ParcelChanges.gdb\ParcelChanges"
    arcpy.Append_management("C:\Work\ParcelBackup\ParcelChanges.gdb\ParcelChanges" + today, "C:\Work\ParcelBackup\ParcelChanges.gdb\ParcelChanges", "NO_TEST", "", "")
    LogMessage(" Field Appended.")


def UpdatePWLayer():

    LogMessage("Update the parcel changes layer on PW...")
    parentVersion = "sde.DEFAULT"
    versionName = "ParcelChanges" + todayhhmm
    arcpy.env.workspace = inWorkspace


    LogMessage("Creating feature layer...")
    arcpy.MakeFeatureLayer_management("PW.PW.ParcelChanges", "PWParcelChanges_Layer")
    LogMessage("Create version for update...")
    arcpy.CreateVersion_management(inWorkspace, "sde.DEFAULT", versionName, "PROTECTED")

    LogMessage("Changing version to " + versionName + "...")
    arcpy.ChangeVersion_management("PWParcelChanges_Layer", "TRANSACTIONAL", "PW." + versionName, "")

   #append the new layer...
    #LogMessage("Appending layer...")
    arcpy.Append_management("C:\Work\ParcelBackup\ParcelChanges.gdb\ParcelChanges" + today, "PWParcelChanges_Layer", "NO_TEST", "", "")
    #arcpy.Append_management("C:\Work\ParcelBackup\ParcelChanges.gdb\ParcelChanges20170609", "PWParcelChanges_Layer", "NO_TEST", "", "")
    # Switch back to DEFAULT version.  This is so we can delete the version.
    LogMessage("Switching back to DEFAULT version...")
    arcpy.ChangeVersion_management("PWParcelChanges_Layer", "TRANSACTIONAL", "sde.DEFAULT", "")

    # Reconcile and post version.
    LogMessage("Reconciling/Posting version " + versionName)
    logFileName = "C:\Work\ParcelBackup\ParcelBackup" + todayhhmm + ".txt"
    arcpy.ReconcileVersions_management(inWorkspace, "ALL_VERSIONS", "sde.DEFAULT", "PW." + versionName,  "LOCK_ACQUIRED", "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_EDIT_VERSION", "POST", "DELETE_VERSION", logFileName)

    return



#Call above features
MakeGDB()
CopyFeatures()
MakeFeatureLayer()
SelectByLocation()
ReverseSelection()
CreateNewFeatureclass()
DeleteFields()
AddField()
UpdatePWLayer()
#test()
