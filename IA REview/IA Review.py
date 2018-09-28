import arcpy
from PWLIB import transcribe
connection = arcpy.env.workspace = "Database Connections/A1_durham-gis.sde"

def main():
    # Layer Creation
    #   City layer for Select by Location on following layers (A1/Admin Boundary/CityLimits)
    #       Remove Child Parcels (Select by Attributes as part of layer creation) (Seando - query)
    #   Parcels in city that have impervious centroid within (A1/Tax/Parcels) - Select by Location - Centroid

    #   Address points in the city limits Select by Location - Intersect with City Limits
    #   All impervious polygons
    arcpy.MakeFeatureLayer_management("Database Connections/A1_durham-gis.sde/GIS_Data.A1.Admin_Boundaries/GIS_Data.A1.Dur_City", "Citylyr")
    print "City Layer"
    arcpy.MakeFeatureLayer_management(connection + "/GIS_Data.A1.AddressFeatures/GIS_Data.A1.ActiveAddressPoints", "APlyr")
    print "AP Layer"
    arcpy.MakeFeatureLayer_management(connection + "/GIS_Data.A1.TaxData/GIS_Data.A1.Parcels", "Parcellyr",
                                      'PIN NOT LIKE \'%.%\'OR PIN LIKE \'%.000\' OR PIN LIKE \'%.L00\' OR PIN LIKE \'%.DO\' OR PIN LIKE \'%.DW\' OR PIN LIKE \'%.DG\' OR PIN LIKE \'%.SPL\' OR PIN LIKE \'%.DUR\'')
    print "Parcel Layer"
    totalParcels = int(arcpy.GetCount_management("parcelLyr")[0])
    print totalParcels

    arcpy.MakeFeatureLayer_management(connection + "/GIS_Data.A1.Impervious_Area/GIS_Data.A1.ImperviousArea", "Implyr")
    print "IA Layer"

    arcpy.SelectLayerByLocation_management("parcelLyr", "INTERSECT", "Citylyr", "", "NEW_SELECTION")
    cityParcels = int(arcpy.GetCount_management("parcelLyr")[0])
    print cityParcels

    # Search cursor on Parcels [@SHAPE, ParcelID]:

    parcelCursor = arcpy.da.SearchCursor("parcelLyr",['PARCEL_ID', 'SHAPE@'])

    print "Layer Preparation Completed. Beginning Processing. \n"

    #   Loop through, select by location Impervious centroid inside and AP inside

    for parcel in parcelCursor:
        arcpy.SelectLayerByLocation_management("APlyr", "INTERSECT", parcel[1], "", "NEW_SELECTION")
        arcpy.SelectLayerByLocation_management("Implyr", "WITHIN", parcel[1], "", "NEW_SELECTION")
        print "\nPARCEL: " + str(parcel[0])
        #       If NO AP, ERROR: No AP, Check PARCEL ID, iterate
        if int(arcpy.GetCount_management("APlyr")[0]) == 0 and int(arcpy.GetCount_management("Implyr")[0]) != 0:
            # print "\tParcel with IA has No Address Points"
            transcribe("Error: Parcel with IA has No Address Point, ParcelID: " + str(parcel[0]))

        #       if No Impervious, break NO ERROR
        elif int(arcpy.GetCount_management("Implyr")[0]) == 0:
            print "\tParcel has no Impervious"
            # transcribe("Error: No Impervious, ParcelID: " + str(parcel[0]))

        else:
            #   Second Search Cursor Address Point Search Cursor [ID]
            #   Third Search Cursor for Impervious [ParcelID, APID]

            APCursor = arcpy.da.SearchCursor("APlyr", ['ID'])

            IACursor = arcpy.da.SearchCursor("Implyr", ['PARCELID', 'ADDRESSPOINT'])
            # grab the first item in the IA list
            next(IACursor)
            i = 0
            #   First loop to find correct AP Referenced for Impervious (Loop through AP)
            #   The correct AP will be the one it lands on, and carried to the next loop
            #
            #       If AP/ID == Impervious/APID then:
            #           break
            #       ELSEIF: i+ 1 == count  BREAK  ERROR No AP/ID == Impervious/APID Check PARCEL ID for AP mismatch
            #
            #       ELSE i++
            for ap in APCursor:
                print "\tAP: " + str(ap[0]), i
                if ap[0] == IACursor[1]:
                    APID = ap[0]
                    print "\tmatch found AP\ID " + str(APID) + ", IA\APID " + str(IACursor[1])
                    break

                elif i+1 >= int(arcpy.GetCount_management("APlyr")[0]):
                    print "\tno match"
                    i += 1
                    break

                else:
                    i+=1
                    print i

            #   IF i < CountAP
            print "\t" + str(i) + " < " + str(arcpy.GetCount_management("APlyr")[0]) + " = " + str(i < arcpy.GetCount_management("APlyr"))
            if i < int(arcpy.GetCount_management("APlyr")[0]):
                print "\tVERIFYING IA AGAINST CONFIRMED AP: " + str(APID) + ", IA count: " + str(arcpy.GetCount_management("Implyr")[0])
                #   Second Loop to ensure correctness (Loop Through Impervious)
                #       if AP/ID != Impervious/APID:
                #           ERROR: Parcel Contains incorrect AP : IMP assignmentgn
                #           Break
                IACursor = arcpy.da.SearchCursor("Implyr", ['PARCELID', 'ADDRESSPOINT'])
                print "\tIA/APID Check:"
                for IA in IACursor:
                    print "\t" + str(IA[1]), str(APID)
                    if str(IA[1]) != str(APID):
                        # print "\tError: IA/Address Point Mismatch, ParcelID: " + parcel[0]
                        transcribe("Error: IA/Address Point Mismatch, ParcelID: " + parcel[0])
                        break
            IACursor = arcpy.da.SearchCursor("Implyr", ['PARCELID', 'ADDRESSPOINT'])
            print "\tIA/PARCEL ID Check:"
            for IA in IACursor:
                print "\t" + str(IA[0]), str(parcel[0])
                if str(IA[0]) != str(parcel[0]):
                    transcribe("Error: IA/Parcel ID Mismatch, ParcelID: " + parcel[0])
                    break


if __name__ == "__main__":
    main()
