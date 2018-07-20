import arcpy
from PWLIB import *
from time import sleep
import sys
#Can we incorporate the pwlib create layers function (or whatever it is called) so that people don't have to know that they need to download the data first?
connection = arcpy.env.workspace = "D:/BackupRepo.gdb"


def main():
    #why do you create the addressLyr here but the parcelLyr inside the addressCheck function?
    arcpy.MakeFeatureLayer_management(connection + "/ActiveAddressPoints",
                                      "addressLyr")
    addressCheck()


def addressCheck():
    print "Beginning Address Check"
    parcelCursor = arcpy.da.SearchCursor(connection + "/Parcels",
                                         ['PARCEL_ID', 'SITE_ADDRE', 'SHAPE@'])
    arcpy.MakeFeatureLayer_management(connection + "/Parcels", "parcelLyr", "PIN NOT LIKE '%.%' OR PIN LIKE '%.000' OR PIN LIKE '%.L00' OR PIN LIKE '%.DO' OR PIN LIKE '%.DW' OR PIN LIKE '%.DG' OR PIN LIKE '%.SPL'")
    totalParcels = int(arcpy.GetCount_management("parcelLyr")[0])
    #Miguel, keep in mind you that this code should not only be clear to you, but to others who read it.  So tell us what you are using i and n for
    i = 0
    n = 0
    for parcel in parcelCursor:
        # logmessage(parcel)
        n+=1
        if i > 3:
            i = 0
        #Miguel, you are using modules that others (including me) aren't familiar with.  yes, people could look them up, but
        # they will learn more if you just tell them.  Always remember you are not working with programmers, or people who
        # aspire to be programmers, so don't hold them to that standard.  If you are going to be "clever" you need to leave
        # breadcrumbs so others can follow you.

        sys.stdout.write("\r[" + str(round(100 * float(n)/float(totalParcels), 2)) + "%]\tWorking" + "%s" % '.' * i)
        sys.stdout.flush()
        arcpy.SelectLayerByLocation_management("addressLyr", "INTERSECT", parcel[2], "", "NEW_SELECTION")
        if int(arcpy.GetCount_management("addressLyr")[0]) == 1:
            apCursor = arcpy.da.SearchCursor("addressLyr", ['ID', 'SITE_ADDRE', 'PARCEL_ID'])  #I added Parcel ID in here because I realized I was checking that too.
            next(apCursor)
            if parcel[1].strip() != apCursor[1].strip():  #explain strip, especially since people may just be familiar with trim.  at some point you won't need to but do it now.
                sys.stdout.write("\r")
                sys.stdout.flush()
                #along the same vein.  for right now i want you to give an example of what the code below will produce
                transcribe("1:1 Address match error: \n\t\tParcelID: " + parcel[0] + ", " + parcel[1] +
                           "\n\t\tAddressPointID: " + str(int(apCursor[0])) + ", " + str(apCursor[1]))
            # let's add a few lines here to compare the parcelIDs.  I suggest you call the transcribe function after you do that.

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