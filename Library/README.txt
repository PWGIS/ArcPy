Version: 0.2.0

Primary Author: Miguel Alan Torres
GIHUB Repo: https://github.com/PWGIS/ArcPy/tree/master/Library

------------------------------------------------------
		FUNCTIONS
------------------------------------------------------
AddressInParcel
(feature_class, final_join)
Bboth arguments are layers that contain the respective items.
Takes a Feature Class and updates the location field and updates
it with the site address of the Address Point contained within the same parcel.
If there is more than one Address Point, it will take the nearest address point to the feature.
If there are no Address Points, it will take the site address sof the parcel.

CreateLayers
(list/string, string)
Takes the name or list of names of feature classes and creates layers if they exist in the feature datasets.

LogMessage
(STRING)
Function writes the STRING argument to the console.
String also prepends the argument with a time stamp.

mergeVersion
(list, string)
Removes the provided layers from the version, reconciles, posts, and attempts to delete the version.
The Parent Version is determined by the version of the current workspace environment variable
If there are any layers still attached to the version, the version will not be deleted.

Transcribe
(STRING, _filepath)
Function writes the STRING argument out to a text file and console.
The file name is the name of the program plus the date that it is run.
The _filepath defaults to the directory of the program being run.
Adding a _filepath STRING argument will overwrite the defaults

UpdateFacilityID
(featurelayer)
Function takes in a feature layer and isolates the highest FACILITYID value.
Then it searches for records with a FACILITYID of NULL and then updates them in sequential order.

versionedLayers
(list, string)
Changes the source of the layers provided to a date-stamped version of the current workspace version.
If the version already exists, it will not create a version but will still change the source of layers provided.


------------------------------------------------------
		UPDATES
------------------------------------------------------
7/5/2018: 	Added the createLayers, mergeVersion, and versionedLayers functions.
6/26/2018: 	BUG FIX - Transcribe now converts data argument into String type. 
6/13/2018: 	BUG FIX - Transcribe now parses for the file name differently.
5/17/2018: 	initial publish to PWGIS
