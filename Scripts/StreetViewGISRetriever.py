#--------------------------------
# Name: StreetViewGISRetriever.py
# Purpose: Take as input a feature class and use the features inside centroids to retrieve street view images from the
# coordinates closest to them and load them into a directory and then optionally associate them with the reference
# feature class.
# Current Owner: David Wasserman
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
import os, sys,arcpy,urllib2

#Define input parameters

# Function Definitions
def do_analysis(*argv):
    """TODO: Add documentation about this function here"""
    Param1=argv[1]
    try:
        #TODO: Add analysis here
        pass
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]
         
# End do_analysis function
 
# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    do_analysis()