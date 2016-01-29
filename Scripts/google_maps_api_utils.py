import urllib, cStringIO
#from PIL import Image
# get arial image from google maps api at coordinates

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
   # TODO(chy): add error handling
   # TODO(chy): investigate returning file rather than string
   # TODO(chy): remove PIL
   # This line is way too long, but python is weird about whitespace. Not sure how to break it up.
   url = """https://maps.googleapis.com/maps/api/streetview?size={0}x{1}&location={2},{3}&fov={4}&heading={5}&pitch={6}&key={7}""".format(size_tuple[0], size_tuple[1], coordinate_pair[0], coordinate_pair[1], fov, heading, pitch, api_key)
   print "Fetching image from:", url
   file = cStringIO.StringIO(urllib.urlopen(url).read())
# #  Image.open(file).show()
   return file


