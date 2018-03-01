import json
import time
import urllib
import urllib2

# TODO
# Read data from csv
# Write data to csv

# THIS MONSTER BELOW IS NEEDED BECAUSE THE STRING TO JSON CONVERSION
# WAS BUGGY, NOT EVEN CLOSE TO UTF-8 ENCODING

def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

def distanceFromBp(fromWhere):
    # The maps_key defined below isn't a valid Google Maps API key.
    # You need to get your own API key.
    # See https://developers.google.com/maps/documentation/timezone/get-api-key
    maps_key = 'AIzaSyB7dsmkO_2ii5DA8iKjYfoTvSl9e881oBo'
    timezone_base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'

    # This joins the parts of the URL together into one string.
    url = timezone_base_url + '?' + urllib.urlencode({
        'origins': fromWhere,
        'destinations': "Budapest",
        'key': maps_key,
    })

    current_delay = 0.1  # Set the initial retry delay to 100ms.
    max_delay = 3600  # Set the maximum retry delay to 1 hour.

    while True:
        try:
            # Get the API response.
            response = str(urllib2.urlopen(url).read())
            # print response
        except IOError:
            pass  # Fall through to the retry loop.
        else:
            # If we didn't get an IOError then parse the result.
            result = json_loads_byteified(response)
            if result['status'] == 'OK':
                return result['rows'][0]['elements'][0]['distance']['value']
            elif result['status'] != 'UNKNOWN_ERROR':
                # Many API errors cannot be fixed by a retry, e.g. INVALID_REQUEST or
                # ZERO_RESULTS. There is no point retrying these requests.
                raise Exception(result['error_message'])

        if current_delay > max_delay:
            raise Exception('Too many retry attempts.')
        print 'Waiting', current_delay, 'seconds before retrying.'
        time.sleep(current_delay)
        current_delay *= 2  # Increase the delay each time we retry.

cities = open('cities.txt', 'r')
for city in cities.readlines():
    print 'Working on ' + city
    distance = distanceFromBp(city)
    print city + ": " + str(distance)