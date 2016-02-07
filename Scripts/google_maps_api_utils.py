import urllib, cStringIO, os
from PIL import Image


def debug(*args):
  """This prints whatever it is given (must be strings) preceded by the name of the file from which it is called.
      Args:
  *args: An arbitrary number of strings
     Returns void."""
  a = [str(b) for b in args]
  print os.path.basename(__file__), " ".join(a)


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


def fetch_streetview_image_and_save(coordinate_pair, heading, path, api_key="", size_tuple=(640, 640), fov=90,
                                    pitch=10):
  """Saves the fetched file if passed a path to save to."""
  image_string = ""
  tries = 0
  image_string = fetch_streetview_image(coordinate_pair, heading, api_key, size_tuple, fov, pitch)
  while tries < 5 and is_error(image_string):
     debug("Error! Trying again. Try #", tries)
     image_string = fetch_streetview_image(coordinate_pair, heading, api_key, size_tuple, fov, pitch)
     tries += 1

  if is_error(image_string):  # Failed to fetch the image.
     debug("Failed to fetch image for coordinates:", coordinate_pair[0], coordinate_pair[1])
     return None

  debug ("Retrieved non-error image! Len:", len(image_string))
  try:
     file = open(os.path.abspath(path), "w")
     file.write(image_string)
     file.close()
  except IOError as error:
     debug("IO error when writing image to", path)
     return None

def is_error(image):
  """Determines whether or not image is one of the known error types returned by the Streetview API.
    Args:
        image: a string representing an image.
    Returns: True if image is an error or an empty string.
             False if it is not.
    Details:
    Unfortunately, the StreetView API doesn't return a HTTP error if it can't find imagery, for some reason
    it actually returns an -image- with error text! There's no reliable programmatic way to determine if it returns
    an error! There are a number of different possible error images. All observed have been gray with text.
    We guess that it's an error if the image length is <30000. The lowest observed length for actual imagery
    is 60000. If this function is returning an error incorrectly, try increasing the threshold length."""
  if image == None or image=="":
    return True
  if len(image) < 20000:
    print len(image)
    return True
  return False
