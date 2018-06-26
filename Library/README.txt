Version: 0.1.0

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
If there are no Address Points, it will take the site address sof the parcel."""

LogMessage
(STRING)
Function writes the STRING argument to the console.
String also prepends the argument with a time stamp.

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

------------------------------------------------------
UPDATES
------------------------------------------------------
6/26/2018: BUG FIX - Transcribe now converts data argument into String type. 
6/13/2018: BUG FIX - Transcribe now parces for the file name differently.
5/17/2018: initial publish to PWGIS
