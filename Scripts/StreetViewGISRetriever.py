# --------------------------------
# Name: StreetViewGISRetriever.py
# Purpose: Take as input a feature class and use the features inside centroids to retrieve street view images from the
# coordinates closest to them and load them into a directory and then optionally associate them with the reference
# feature class.
# Current Owner: David Wasserman & chy
# Last Modified: 01/01/2016
# Copyright:   (c) CoAdapt
# ArcGIS Version:   10.3
# Python Version:   2.7
# --------------------------------
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
import os, arcpy, urllib, cStringIO,math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

# Define input parameters
InputFeatureClass = r"C:\Users\anthr_000\Documents\My Education\GIS and Modeling\GIS Programming-ArcPy\Scripts\StreetViewGeoprocessing\ToolData.gdb\hillsborough_Sample_RdsData"#arcpy.GetParameterAsText(1)
OutputImageDirectory =r""#arcpy.GetParameterAsText(2)
UniqueFieldForImageNames = r"ExplodeID"#arcpy.GetParameterAsText(3)
GoogleAPIKey = r""#arcpy.GetParameter(4)  # String
OptHeadingField=r""#arcpy.GetParameterAsText(5)
AssociateAttachmentsBool = r""#arcpy.GetParameter(6)  # Boolean


# Worker Function Definitions
def debug(*args):
    """This prints whatever it is given (must be strings) preceded by the name of the file from which it is called.
        Args:
    *args: An arbitrary number of strings
       Returns void."""
    print os.path.basename(__file__), " ".join(args)


def fetch_streetview_image(coordinate_pair, heading, api_key="", size_tuple=(640, 640), fov=90, pitch=10):
    """ Fetches an image from the Google StreetView API. (https://developers.google.com/maps/documentation/streetview/intro)
       Args:
          coordinate_pair: a tuple (x, y)
          api_key: optional on the API's standard usage plan (<25000 queries/day).
             See https://developers.google.com/maps/documentation/streetview/get-api-key)
          heading: compass heading of the camera
          size_tuple: output size of the image. Max is 640x640 (on the standard plan).
          fov: field of view. Horizontal field of view of the image.
          pitch: Vertical angle of the camera relative to the Street View vehicle. Set to 10 (appx horizontal) because 0
             frequently includes part of the vehicle in the image.
       Returns:
          file: string representation of the image file.
    """
    # This line is way too long, but python is weird about whitespace. Not sure how to break it up.
    url = """https://maps.googleapis.com/maps/api/streetview?size={0}x{1}&location={2},{3}&fov={4}&heading={5}&pitch={6}&key={7}""".format(
            size_tuple[0], size_tuple[1], coordinate_pair[0], coordinate_pair[1], fov, heading, pitch, api_key)
    debug("Fetching image from:", url)
    try:
        return urllib.urlopen(url).read()
    except:
        debug("Failed to fetch StreetView image for coordinates:", coordinate_pair)
        return None


def fetch_streetview_image_and_save(coordinate_pair, heading, path, api_key="", size_tuple=(640, 640), fov=90, pitch=10):
    """Saves the fetched file if passed a path to save to."""
    image_string = fetch_streetview_image(coordinate_pair, heading, api_key, size_tuple, fov, pitch)
    try:
        file = open(os.path.abspath(path), "w")

        file.write(image_string)
        file.close()
        pass
    except IOError as error:
        debug("IO error when writing image to", file)
        return None

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

def getAngleBetweenPoints(point1,point2,headingMode=True,invertDegrees=False):
    point1CentX=point1.centroid.X
    point2CentX=point2.centroid.X
    point1CentY=point1.centroid.Y
    point2CentY=point2.centroid.Y
    print(point1CentX)
    diffX=point2CentX-point1CentX
    diffY=point2CentY-point1CentY
    if diffX==0 and diffX and diffY:
        print("No heading could be achieved because value was 0.")
        return 0
    invertWPi=0
    if invertDegrees:
        invertWPi=math.pi
    if headingMode:
        return math.degrees(math.atan2(diffX,diffY)-invertWPi)%360
    else:
        return math.degrees(math.atan2(diffX,diffY)-invertWPi)
# PUT API FUNCTION HERE

# Function Definitions
def do_analysis(inFC, outDir, uniqueNameField, googleMapsAPIKey, heading=0,attachmentBool=True):
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
        featurePathField = arcpy.ValidateFieldName("UniqueFeatPaths", workspace)
        AddNewField(inFC, featurePathField, "TEXT")
        arcPrint("Gathering feature information.", True)
        # Get feature description and spatial reference information for tool use
        desc = arcpy.Describe(inFC)
        spatialRef = desc.spatialReference
        shpType = desc.shapeType
        srName = spatialRef.name
        arcPrint(
                "The shape type is {0}, and the current spatial reference is: {1}".format(str(shpType), str(srName)),
                True)
        WGS_1984_MajAux=arcpy.SpatialReference(104199) #http://support.esri.com/cn/knowledgebase/techarticles/detail/34749
        fNames = ["SHAPE@", uniqueNameField, featurePathField]
        if heading and FieldExist(inFC,heading):
            fNames.append(heading)

        if shpType == "Polyline":
            with arcpy.da.UpdateCursor(inFC, fNames,spatial_reference=WGS_1984_MajAux) as cursor:
                for row in cursor:
                    print("Point 1 and 2")
                    midPoint=row[getFIndex(fNames,"SHAPE@")].positionAlongLine(.5,True)
                    beyondMidPoint= row[getFIndex(fNames,"SHAPE@")].positionAlongLine(.500001,True)
                    headingParam= getAngleBetweenPoints(midPoint,beyondMidPoint,True)
                    midpointProjected=midPoint.projectAs(WGS_1984_MajAux)
                    fileOutPath=os.path.join(outDir,"{0}.{1}".format(str(uniqueNameField),"jpg"))
                    streetViewString=fetch_streetview_image_and_save((midpointProjected.centroid.Y,midpointProjected.centroid.X),headingParam,fileOutPath)


        else:
            with arcpy.da.UpdateCursor(inFC, fNames, spatial_reference=WGS_1984_MajAux) as cursor:
                for row in cursor:
                    midLabelPoint=row[getFIndex(fNames,"SHAPE@")].labelPoint
                    midLabelPointProjected=midLabelPoint.projectAs(WGS_1984_MajAux)
                    headingParam= row[getFIndex(fNames,heading)] if heading in fNames  else None
                    if headingParam:
                        fetch_streetview_image_and_save((midLabelPointProjected.centroid.Y,midLabelPointProjected.centroid.X),headingParam)
                    else:
                        fetch_streetview_image_and_save((midLabelPointProjected.centroid.Y,midLabelPointProjected.centroid.X))

        arcPrint("Cleaning up intermediates.", True)
        del spatialRef, desc, cursor, WGS_1984_MajAux
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
    except Exception as e:
        print(e.args[0])


# End do_analysis function

# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script-Only calls on main function call.
if __name__ == '__main__':
    do_analysis(InputFeatureClass, OutputImageDirectory, UniqueFieldForImageNames, GoogleAPIKey,
                AssociateAttachmentsBool)
