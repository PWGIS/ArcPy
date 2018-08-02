import arcpy
from PWLIB import *
from time import sleep
import sys
#Can we incorporate the pwlib create layers function (or whatever it is called) so that people don't have to know that they need to download the data first?
connection = arcpy.env.workspace = "D:/BackupRepo.gdb"


def main():
    #why do you create the addressLyr here but the parcelLyr inside the addressCheck function?

    addressCheck()


def addressCheck():
    print "Beginning Address Check"
    parcelCursor = arcpy.da.SearchCursor(connection + "/Parcels",
                                         ['PARCEL_ID', 'SITE_ADDRE', 'SHAPE@'])
    arcpy.MakeFeatureLayer_management(connection + "/ActiveAddressPoints",
                                      "addressLyr")
    arcpy.MakeFeatureLayer_management(connection + "/Parcels", "parcelLyr",
                                      "PIN NOT LIKE '%.%' OR PIN LIKE '%.000' OR PIN LIKE '%.L00' OR PIN LIKE '%.DO' "
                                      "OR PIN LIKE '%.DW' OR PIN LIKE '%.DG' OR PIN LIKE '%.SPL'")
    totalParcels = int(arcpy.GetCount_management("parcelLyr")[0])
    i = 0  # i is used in the progress bar to keep track of the number of '.' following "WORKING"
    n = 0  # n is number of parcels checked, this is for the percentage in progress bar
    for parcel in parcelCursor:
        # logmessage(parcel)
        n+=1
        if i > 3:
            i = 0

        # sys.stdout is the low-level print function that allows you to have more control of the output
        # as a result, it is able to write a line without moving to the next line.
        # In all cases this is used for the progress bar or to operate around it.
        sys.stdout.write("\r[" + str(round(100 * float(n)/float(totalParcels), 2)) + "%]\tWorking" + "%s" % '.' * i)
        sys.stdout.flush()
        arcpy.SelectLayerByLocation_management("addressLyr", "INTERSECT", parcel[2], "", "NEW_SELECTION")
        if int(arcpy.GetCount_management("addressLyr")[0]) == 1:
            apCursor = arcpy.da.SearchCursor("addressLyr", ['ID', 'SITE_ADDRE', 'PARCEL_ID'])
            next(apCursor)
            # .strip is a string method that removes the "empty space" flanking both sides of a string.
            # e.g., "       This      " becomes "This"
            if parcel[1].strip() != apCursor[1].strip():
                sys.stdout.write("\r")
                sys.stdout.flush()
                # when the Parcel address doesn't match the AP address or the Parcel IDs do not match
                # it will print the Parcel and AddressPoint ID their respective addresses and the AP parcel ID
                transcribe("1:1 Address match error: \n\t\tParcelID: " + parcel[0] + ", " + parcel[1] +
                           "\n\t\tAddressPointID: " + str(int(apCursor[0])) + ", " + str(apCursor[1]))
            if parcel[0] != apCursor[2]:
                sys.stdout.write("\r")
                sys.stdout.flush()
                # when the Parcel address doesn't match the AP address or the Parcel IDs do not match
                # it will print the Parcel and AddressPoint ID their respective addresses and the AP parcel ID
                transcribe("1:1 Parcel_ID match error: \n\t\tParcelID: " + parcel[0] +
                           "\n\t\tAddressPointPID: " + str(int(apCursor[0])) + ", " + str(int(apCursor[2])))

        #As we just discussed i don't think we should compare the site addresses when there is more than one address point on a parcel since
        # most of those address points won't match and, according to Carmen, there's no way to identify the master address point by the attributes
        # i've added in the parcel id for the search cursor.  essentially we could just remove the 'Site_Addre' from the cursor and then
        # change the for ap in apCursor to "if parcel[1] == ap[1]:"
        elif int(arcpy.GetCount_management("addressLyr")[0]) > 1:
            apCursor = arcpy.da.SearchCursor("addressLyr", ['ID', 'SITE_ADDRE', 'PARCEL_ID'])
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