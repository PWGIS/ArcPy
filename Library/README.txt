addressinparcel(feature_class, final_join):
Bboth arguments are layers that contain the respective items.
Takes a Feature Class and updates the location field and updates
it with the site address of the Address Point contained within the same parcel.
If there is more than one Address Point, it will take the nearest address point to the feature.
If there are no Address Points, it will take the site address sof the parcel."""

logmessage(STRING)
Function writes the STRING argument to the console.
String also prepends the argument with a time stamp.

transcribe(STRING, file_path*)
Function writes the STRING argument out to a text file and console.
The file name is the name of the program plus the date that it is run.
The file_path defaults to the directory of the program being run.
Adding a file_path STRING argument will overwrite the defaults

