import arcpy, time, os


def logmessage(message):
    """ARGS:
    message: a string variable to be written to the file and console

    DESCRIPTION:
    Function writes the STRING argument to the console.
    String also prepends the argument with a time stamp."""
    print time.strftime ("%H:%M", time.localtime()) + "\t" + str(message)
    return


def transcribe(message, _filepath=os.path.dirname(__file__) + "/"):
    """ ARGS:
    message: a string variable to be written to the file and console
    _filepath: the location of the directory to write the file to, assumes '/' notation
        default location is the same directory that the program is being run from.

    DESCRIPTION:
    Function writes the STRING argument out to a text file and console.
    The file name is the name of the program plus the date that it is run.
    The file_path defaults to the directory of the program being run.
    Adding a file_path STRING argument will overwrite the defaults

    DEPENDENCIES:
    Utilizes the logmessage function to write to console.
    """
    txt_file = open(_filepath + os.path.splitext(os.path.basename(__file__))[0] +
                    "_" + time.strftime("%Y-%m-%d", time.localtime()) + ".txt", "a")
    txt_file.write(time.strftime("%H:%M", time.localtime()) + "\t" + str(message) + "\n")
    logmessage(message)
    txt_file.close()


def updatefacilityid(featurelayer):
    """ ARGS:
    featurelayer: A reference to a layer that contains the featureclass that has to be updated.

    DESCRIPTION:
    Function takes in a feature layer and isolates the highest FACILITYID value.
    Then it searches for records with a FACILITYID of NULL and then updates them
        in sequential order."""
    # Find the max value here, if we get nothing then quit.
    print "Create Search Cursor"
    rows = arcpy.SearchCursor(featurelayer, "", "", "", "FACILITYID D")
    row = rows.next()
    if row is None:
        del rows
        del row
        return

    maxId = row.getValue("FACILITYID")
    if maxId is None:
        maxId = 0
    # convert the id to an integer
    newId = int(maxId) + 1

    # Create update cursor for feature class, only for those features whose FACILITYID is NULL.
    rows = arcpy.UpdateCursor(patchfeatures, "FACILITYID IS NULL")

    # Now update the FACILITYIDs for those features...
    for row in rows:
        row.setValue('FACILITYID', newId)
        rows.updateRow(row)
        newId = newId + 1

    # Delete cursor and row objects to remove locks on the data
    del rows


if __name__ == "__main__":
    logmessage("is this working?")
    transcribe(2+3)
