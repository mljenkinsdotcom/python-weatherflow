import requests

# Define data formats so we can convert observations from integer arrays to dictionaries
_OBS_AIR = ('timestamp',
            'barometric_pressure',
            'air_temperature',
            'relative_humidity',
            'lightning_strike_count',
            'lightning_strike_avg_distance',
            'battery_volts',
            'report_interval')
_OBS_SKY = ('timestamp',
            'brightness',
            'uv',
            'precip_accum_last_1hr',
            'wind_lull',
            'wind_avg',
            'wind_gust',
            'wind_direction',
            'battery_volts',
            'report_interval',
            'solar_radiation',
            'precip_accum_local_day',
            'precip_type',
            'wind_interval',
            'precip_accum_local_yesterday_final',
            'precip_minutes_local_yesterday_final',
            'precip_analyze_type')
_OBS_ST =  ('timestamp',
            'wind_lull',
            'wind_avg',
            'wind_gust',
            'wind_direction',
            'wind_interval',
            'barometric_pressure',
            'air_temperature',
            'relative_humidity',
            'brightness',
            'uv',
            'solar_radiation',
            'precip_accum_last_1hr',
            'precip_type',
            'lightning_strike_avg_distance',
            'lightning_strike_count',
            'battery_volts',
            'report_interval',
            'precip_accum_local_day',
            'precip_accum_local_yesterday_final',
            'precip_minutes_local_yesterday_final',
            'precip_analyze_type')


class Rest:
    def __init__(self, access_token=None, api_key=None, station_id=None, device_id=None, debug=False):
        """
        This classes utilizes the WeatherFlow REST API and requires an api key or oauth token to connect
        :param access_token: private user oauth access (bearer) token for user from oauth2 implicit flow
        :param api_key: api key for acquiring public data
        :param station_id: default station id to make requests for (to avoid having to pass each time)
        :param device_id: default device id to make requests for (to avoid having to pass each time)
        :param debug: Enable HTTP debugging for low-level troubleshooting
        """
        self.debug = debug
        if debug:
            self._enable_requests_debug()
            print("Constructing REST class")

        # WeatherFlow REST API parameters
        self.baseurl = 'https://swd.weatherflow.com/swd/rest'
        self.baseheaders = {'Accept': 'application/json'}
        self.baseparams = {}

        # Deal with security (authorization)
        if access_token:
            self.baseheaders['Authorization'] = "Bearer " + access_token
        elif api_key:
            self.baseparams['api_key'] = api_key
        else:
            raise UsageError("No REST credentials specified")

        # Set default values if provided
        self.station_id = station_id
        self.device_id = device_id

    def get_device_observations(self, device_id=None, day_offset=None, time_start=None, time_end=None, format=None,
                                auto_convert=True):
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
        :param auto_convert: If true, observations will be converted from an array of integers to a dictionary
        :return: JSON from WeatherFlow API
        """
        if not device_id:
            device_id = self.device_id

        url = self.baseurl + '/observations/device/' + str(device_id)
        headers = self.baseheaders
        params = self.baseparams
        if day_offset:
            params['day_offset'] = day_offset
        if time_start:
            params['time_start'] = time_start
        if time_end:
            params['time_end'] = time_end
        if format:
            params['format'] = format

        r = self._get(url, headers=headers, params=params)
        pr = r.json()

        # Auto convert observation data from array of integers to dictionary
        if auto_convert:
            obsdata = pr['obs']
            obstype = pr['type']
            pr['obs'] = []
            for obs in obsdata:
                pr['obs'].append(self.convert_obs(obs, obstype))

        return pr

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

        url = self.baseurl + '/observations/station/' + str(station_id)
        headers = self.baseheaders
        params = self.baseparams

        r = self._get(url, headers=headers, params=params)
        return r.json()

    def get_stations(self):
        """
        Smart Weather Devices all belong to a Station. This response contains Station metadata and metadata for the
        Devices in it. Each user can create multiple Stations. A Device can only be in one Station at a time.

        Only devices with a serial_number value can send new observations. A Device wihout a serial_number indicates
        that Device is no longer active.
        :return: JSON from WeatherFlow API
        """
        url = self.baseurl + '/stations'
        headers = self.baseheaders
        params = self.baseparams

        r = self._get(url, headers=headers, params=params)
        return r.json()

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

        url = self.baseurl + '/stations/' + str(station_id)
        headers = self.baseheaders
        params = self.baseparams

        r = self._get(url, headers=headers, params=params)
        return r.json()

    def _get(self, url, headers=None, params=None):
        """
        Helper method to make REST call, this allows us to more gracefully deal with any errors
        :param url: URL to get
        :param headers: Request headers to pass
        :param params: Request parameters to pass on query string
        :return: Results of request
        """
        try:
            r = requests.get(url, headers=headers, params=params)
        except:
            raise RestError

        if r.status_code == 200:
            return r
        else:
            raise RestError("WeatherFlow REST Get Error StatusCode=%s Reason=%s" % (r.status_code, r.reason))

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
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    @staticmethod
    def convert_obs(obs, obs_type):
        """
        Convert an observation from an array of integers to a dictionary
        :param obs: Observation obtained from WeatherFlow API to convert
        :param obs_type: Observation type as obtained from WeatherFlow API (obs_air, obs_sky, obs_st)
        :return: Dictionary containing observation
        """
        retobj = {}
        dkeys = ()
        if obs_type == 'obs_air':
            dkeys = _OBS_AIR
        elif obs_type == 'obs_sky':
            dkeys = _OBS_SKY
        elif obs_type == 'obs_st':
            dkeys = _OBS_ST
        else:
            raise UsageError("Invalid observation type specified")

        for i, key in enumerate(dkeys, start=0):
            retobj[key] = obs[i]

        return retobj


class RestError(Exception):
    pass


class UsageError(Exception):
    pass
