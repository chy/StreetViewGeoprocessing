import urllib, cStringIO, os

# This prints whatever it is given (must be strings) preceded by the name of the file from which it is called.
# Args:
#   *args: An arbitrary number of strings
# Returns void.
def debug(*args):
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


def fetch_streetview_image(
        coordinate_pair, heading, path, api_key="", size_tuple=(640, 640), fov=90, pitch=10):
  image_string = fetch_streetview_image(coordinate_pair, heading, api_key, size_tuple, fov, pitch)
  try:
    file = open(os.path.abspath(path), "w")
    file.write(image_string)
    file.close()
    pass
  except IOError as error:
    debug("IO error when writing image to", filename)
    return None
