#--------------------------------
# Name: StreetViewGISRetriever.py
# Purpose: Take as input a feature class and use the features inside centroids to retrieve street view images from the
# coordinates closest to them and load them into a directory and then optionally associate them with the reference
# feature class.
# Current Owner: David Wasserman & chy
# Last Modified: 01/01/2016
# Copyright:   (c) CoAdapt
# ArcGIS Version:   10.3
# Python Version:   2.7
#--------------------------------
 # Copyright 2016  David J. Wasserman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------
# Import Modules
import os, sys,arcpy,urllib2,cStringIO

#Define input parameters
InputFeatureClass=arcpy.GetParameterAsText(1)
OutputImageDirectory=arcpy.GetParameterAsText(2)
UniqueFieldForImageNames=arcpy.GetParameterAsText(3)
GoogleAPIKey=arcpy.GetParameter(4)#String
AssociateAttachmentsBool=arcpy.GetParameter(5) #Boolean
# Worker Function Definitions
def getFIndex(field_names, field_name):
    try:  # Assumes string will match if all the field names are made lower case.
        return [str(i).lower() for i in field_names].index(str(field_name).lower())
        # Make iter items lower case to get right time field index.
    except:
        print("Couldn't retrieve index for {0}, check arguments.".format(str(field_name)))
        return None

def arcPrint(string, progressor_Bool=False):
    # This function is used to simplify using arcpy reporting for tool creation,if progressor bool is true it will
    # create a tool label.
    try:
        if progressor_Bool:
            arcpy.SetProgressorLabel(string)
            arcpy.AddMessage(string)
            print(string)
        else:
            arcpy.AddMessage(string)
            print(string)
    except arcpy.ExecuteError:
        arcpy.GetMessages(2)
    except:
        arcpy.AddMessage("Could not create message, bad arguments.")


def FieldExist(featureclass, fieldname):
    # Check if a field in a feature class field exists and return true it does, false if not.
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount >= 1):  # If there is one or more of this field return true
        return True
    else:
        return False


# CR: add comment describing functionality and parameter purposes (apply to all instances)
def AddNewField(in_table, field_name, field_type, field_precision="#", field_scale="#", field_length="#",
                field_alias="#", field_is_nullable="#", field_is_required="#", field_domain="#"):
    # Add a new field if it currently does not exist...add field alone is slower than checking first.
    if FieldExist(in_table, field_name):
        print(field_name + " Exists")
        arcpy.AddMessage(field_name + " Exists")
    else:
        print("Adding " + field_name)
        arcpy.AddMessage("Adding " + field_name)
        arcpy.AddField_management(in_table, field_name, field_type, field_precision, field_scale,
                                  field_length,
                                  field_alias,
                                  field_is_nullable, field_is_required, field_domain)
#PUT API FUNCTION HERE

# Function Definitions
def do_analysis(inFC,outDir,uniqueNameField,googleMapsAPIKey,attachmentBool=True):
    """This is the main function call for the StreetViewGISRetrieval Tool. It interacts with the Google Maps API and
    the ArcGIS Arcpy library to fill a directory with street view images that correspond to an input feature's
    inside centroids."""
    try:
        arcpy.env.overwriteOutput = True
        workspace = os.path.dirname(inFC)
        FileName = os.path.basename(inFC)
        # tempOutName = arcpy.ValidateTableName("TempBlockFC_1", workspace)
        # tempOutFeature = os.path.join(workspace, tempOutName)
        # Add New Fields
        arcPrint("Adding new field for Image paths, will change if images location change.", True)
        featurePathField = arcpy.ValidateFieldName("UniqueFeatPaths",workspace)
        AddNewField(inFC,featurePathField,"TEXT")
        arcPrint("Gathering feature information.", True)
        # Get feature description and spatial reference information for tool use
        desc = arcpy.Describe(inFC)
        spatialRef = desc.spatialReference
        shpType = desc.shapeType
        srName = spatialRef.name
        with arcpy.da.UpdateCursor(inFC,["SHAPE@","SHAPE@LENGTH",featurePathField]) as cursor:
            for row in cursor:
                print row

        arcpy.FeatureToPoint_management(inFC,)
        pass
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]
         
# End do_analysis function
 
# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script-Only calls on main function call.
if __name__ == '__main__':
    do_analysis(InputFeatureClass,OutputImageDirectory,UniqueFieldForImageNames,GoogleAPIKey,AssociateAttachmentsBool)