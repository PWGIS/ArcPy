import arcpy
from PWLIB import *
from time import sleep
import sys
connection = arcpy.env.workspace = "D:/BackupRepo.gdb"


def main():
    arcpy.MakeFeatureLayer_management(connection + "/ActiveAddressPoints",
                                      "addressLyr")
    addressCheck()


def addressCheck():
    print "Beginning Address Check"
    parcelCursor = arcpy.da.SearchCursor(connection + "/Parcels",
                                         ['PARCEL_ID', 'SITE_ADDRE', 'SHAPE@'])
    arcpy.MakeFeatureLayer_management(connection + "/Parcels", "parcelLyr")
    totalParcels = int(arcpy.GetCount_management("parcelLyr")[0])
    i = 0
    n = 0
    for parcel in parcelCursor:
        # logmessage(parcel)
        n+=1
        if i > 3:
            i = 0
        sys.stdout.write("\r[" + str(round(100 * float(n)/float(totalParcels), 2)) + "%]\tWorking" + "%s" % '.' * i)
        sys.stdout.flush()
        arcpy.SelectLayerByLocation_management("addressLyr", "INTERSECT", parcel[2], "", "NEW_SELECTION")
        if int(arcpy.GetCount_management("addressLyr")[0]) == 1:
            apCursor = arcpy.da.SearchCursor("addressLyr", ['ID', 'SITE_ADDRE'])
            next(apCursor)
            if parcel[1].strip() != apCursor[1].strip():
                sys.stdout.write("\r")
                sys.stdout.flush()
                transcribe("1:1 Address match error: \n\t\tParcelID: " + parcel[0] + ", " + parcel[1] +
                           "\n\t\tAddressPointID: " + str(int(apCursor[0])) + ", " + str(apCursor[1]))
        elif int(arcpy.GetCount_management("addressLyr")[0]) > 1:
            apCursor = arcpy.da.SearchCursor("addressLyr", ['ID', 'SITE_ADDRE'])
            for ap in apCursor:
                if parcel[1].strip() == ap[1].strip():
                    break
            else:
                sys.stdout.write("\r")
                sys.stdout.flush()
                transcribe("1:X Address match error: \n\t\tParcelID: " + parcel[0] + ", " + parcel[1] +
                           "\n\t\tMultiple Address Points. Count: " + str(arcpy.GetCount_management("addressLyr")[0]))
        else:
            pass
            # sys.stdout.write("\r")
            # sys.stdout.flush()
            # transcribe("1:0 Address Point Count Error!\n\t\tParcelID:" + parcel[0] + ", " + parcel[1] +
            #            "\n\t\tNo Address Point in Parcel.")
        i += 1
main()