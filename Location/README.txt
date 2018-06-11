
                                 Location.py

 PURPOSE:

Calculate a value for the location field for those features where the current value is Null.


 1).   Pass in a feature class, feature dataset, or list of feature classes on which you want the calculation performed.
       Layers are created for each feature class and two lists are created--one for feature classes where the field
       name is LOCATION and one where the field name is LOCATIONDESCRIPTION.  These lists are appended to another list.

 2).   A new version is created and the layers created in Step 1 are switched to the new version.

 3).   Loop through the list of layers, do a spatial join with the parcel layer for those features inside a parcel, creating
       an in-memory feature class.

 4).   Iterate through this in-memory feature class using a search cursor.  Use the FacilityID to select the specific
       feature in the layer.  Use the ParcelID to identify any address points in the parcel.  If there is one, transfer
       its site address to the selected feature in the layer.  If there is more than one address poing create an in-memory 
       feature class to find the nearest and transfer its site address to the selected feature.  if there are no address points
       transfer the parcel site address to the selected feature.
     

 5).   Loop through the list of layers, initially using Select by Attributes to select only those features that still have a 
       null location field.  Do a spatial join with the parcel layer to create an in-memory feature class, joinClosest.  use a search
       cursor to iterate through joinClosest, retrieving the the FacilityID and selecting the specific feature in the layer. Calculate
       the location field using the site address in the joinClosest feature class. 


 -----------------------------------------------------------------------------

 DEPENDENCIES:

 1).  ArcMap 10.1 or higher.

 2).  A database connection to the Publicworks server.



 -----------------------------------------------------------------------------
 INPUT(S):

 1). A feature class, a feature dataset, or a list of feature classes (see note #1 below) and an indication as to the data type you are passing in.


 -----------------------------------------------------------------------------
 OUTPUT(S):

 1). See Purpose above for Outputs.

 -----------------------------------------------------------------------------
 NOTES:

 TODO ITEMS (in no particular order)
 1).  What if the list passed into the createLayers function consists of both feature classes and feature datasets?
 2).  Once all the items in a list have been handled we want to break out of the loop and move to the next function.  that isn't working.
 3).  If we pass in a feature dataset, how do we handle feature classes that we want to skip, like soScadaSensor?
 4).  Join the joinClosest back to the layer based on the facilityID and then calculate the value of the location field from the site address


 -----------------------------------------------------------------------------

 -----------------------------------------------------------------------------
 HISTORY:

 2017-eno: initial coding
 201805-eno: revisions to overall script
 201805-torres: wrote initial address in parcel function
 20180607-revisions completed to script, incorporating address in parcel function and changing create layers function so that a variety of data types
          can be passed into the function.

 ==============================================================================