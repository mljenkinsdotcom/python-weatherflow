import requests
from .data import add_data_keys

# Define REST API parameters
_REST_BASE_URL = 'https://swd.weatherflow.com/swd/rest'


class Rest:
    def __init__(self, access_token=None, api_key=None, station_id=None, device_id=None, base_url=_REST_BASE_URL,
                 debug=False):
        """
        This classes utilizes the WeatherFlow REST API and requires an api key or oauth token to connect
        :param access_token: private user oauth access (bearer) token for user from oauth2 implicit flow
        :param api_key: api key for acquiring public data
        :param station_id: default station id to make requests for (to avoid having to pass each time)
        :param device_id: default device id to make requests for (to avoid having to pass each time)
        :param base_url Base URL of WeatherFlow REST API to use
        :param debug: Enable HTTP debugging for low-level troubleshooting
        """
        self.debug = debug
        if debug:
            self._enable_requests_debug()
            print('Constructing REST class')

        # WeatherFlow REST API parameters
        self.base_url = base_url
        self.base_headers = {'Accept': 'application/json'}
        self.base_params = {}

        # Deal with security (authorization)
        if access_token:
            self.base_headers['Authorization'] = 'Bearer ' + access_token
        elif api_key:
            self.base_params['api_key'] = api_key
        else:
            raise UsageError('No REST credentials specified')

        # Set default values if provided
        self.station_id = station_id
        self.device_id = device_id

    def get_device_observations(self, device_id=None, day_offset=None, time_start=None, time_end=None, format=None,
                                auto_add_data_keys=True):
        """
        Get observations for a Device(Air,Sky,Tempest) by using the device_id as the key. You can find device_id values
        in the response from the Stations service You can get observations using several filters
        (latest, time range, day offset).

        Use the "type" value to determine the layout of the observations values. The "obs" object is an array of
        observations. Each observation is an array of observation values (see layout below).
        :param device_id: device to acquire data for
        :param day_offset:  TIME FILTER - Get an entire day of observations by UTC day offset.
                            0 - Current day UTC
                            1 - Yesterday UTC
        :param time_start:  TIME FILTER - Time range start time epoch seconds UTC.
                            Observation data at 1 minute time resolution is available for a time range that is <= 5 days
                            You also need to send "time_end".
                            This field pair is optional.
                            If the request does not contain any time filters only the latest observation is returned
        :param time_end:    TIME FILTER - Time range start time epoch seconds UTC.
                            Observation data at 1 minute time resolution is available for a time range that is <= 5 days
                            You also need to send "time_start".
                            This field pair is optional.
                            If the request does not contain any time filters only the latest observation is returned
        :param format: Use format=csv to return a CSV response type.
        :param auto_add_data_keys: If true, data arrays will be converted from integer arrays to dictionaries
        :return: JSON from WeatherFlow API
        """
        if not device_id:
            device_id = self.device_id

        url = self.base_url + '/observations/device/' + str(device_id)
        headers = self.base_headers
        params = self.base_params
        if day_offset:
            params['day_offset'] = day_offset
        if time_start:
            params['time_start'] = time_start
        if time_end:
            params['time_end'] = time_end
        if format:
            params['format'] = format

        result = self._get(url, headers=headers, params=params).json()

        if auto_add_data_keys:
            return add_data_keys(result, 'rest')
        else:
            return result

    def get_station_observation(self, station_id=None):
        """
        Get the latest federated observation for a Station. This observation is made from the latest Device
        observations that belong to the Station. If a user has multiple Devices of the same type they are able to
        designate one of them as primary. This is the one used to make the federated observation.

        A user can also designate each device as either indoor or outdoor. All indoor observation value fields will
        end with an "_indoor" suffix. Outdoor observations fields do not have a suffix.

        The station_units values represent the units of the Station's owner, not the units of the observation values
        in the API response.
        :param station_id: station to acquire data for
        :return: JSON from WeatherFlow API
        """
        if not station_id:
            station_id = self.station_id

        url = self.base_url + '/observations/station/' + str(station_id)
        headers = self.base_headers
        params = self.base_params

        result = self._get(url, headers=headers, params=params)
        return result.json()

    def get_stations(self):
        """
        Smart Weather Devices all belong to a Station. This response contains Station metadata and metadata for the
        Devices in it. Each user can create multiple Stations. A Device can only be in one Station at a time.

        Only devices with a serial_number value can send new observations. A Device wihout a serial_number indicates
        that Device is no longer active.
        :return: JSON from WeatherFlow API
        """
        url = self.base_url + '/stations'
        headers = self.base_headers
        params = self.base_params

        result = self._get(url, headers=headers, params=params)
        return result.json()

    def get_station(self, station_id=None):
        """
        Smart Weather Devices all belong to a Station. This response contains Station metadata and metadata for the
        Devices in it. Each user can create multiple Stations. A Device can only be in one Station at a time.

        Only devices with a serial_number value can send new observations. A Device wihout a serial_number indicates
        that Device is no longer active.

        :param station_id: station to acquire data for
        :return: JSON from WeatherFlow API
        """
        if not station_id:
            station_id = self.station_id

        url = self.base_url + '/stations/' + str(station_id)
        headers = self.base_headers
        params = self.base_params

        result = self._get(url, headers=headers, params=params)
        return result.json()

    def _get(self, url, headers=None, params=None):
        """
        Helper method to make REST call, this allows us to more gracefully deal with any errors
        :param url: URL to get
        :param headers: Request headers to pass
        :param params: Request parameters to pass on query string
        :return: Results of request
        """
        try:
            result = requests.get(url, headers=headers, params=params)
        except:
            raise RestError

        if result.status_code == 200:
            return result
        else:
            raise RestError('WeatherFlow REST Get Error StatusCode=%s Reason=%s' % (result.status_code, result.reason))

    @staticmethod
    def _enable_requests_debug():
        """
        Enable debugging to output all HTTP data sent
        :return: Nothing
        """
        import logging

        try:
            import http.client as http_client
        except ImportError:
            # Python 2
            import httplib as http_client
        http_client.HTTPConnection.debuglevel = 1

        # You must initialize logging, otherwise you'll not see debug output.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger('requests.packages.urllib3')
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True


class RestError(Exception):
    pass


class UsageError(Exception):
    pass
