# Define format for REST API fields so we can convert data from integer arrays to dictionaries (e.g. observation data)
REST_DATA_FORMAT = {'obs_air': {'obs': (    'timestamp',
                                            'barometric_pressure',
                                            'air_temperature',
                                            'relative_humidity',
                                            'lightning_strike_count',
                                            'lightning_strike_avg_distance',
                                            'battery_volts',
                                            'report_interval')},
                   'obs_sky': { 'obs': (   'timestamp',
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
                                            'precip_analyze_type')},
                   'obs_st': { 'obs': (     'timestamp',
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
                                            'precip_analyze_type')}}

# TODO: Define format for Websocket fields so we can convert data from integer arrays to dictionaries (e.g. observation data)
WS_DATA_FORMAT = {}

# TODO: Define format for UDP fields so we can convert data from integer arrays to dictionaries (e.g. observation data)
UDP_DATA_FORMAT = {'rapid_wind': {'ob': ('timestamp', 'wind_gust', 'wind_direction')}}


# TODO: Update values for UDP format
"""
obs_st
Index	Field	Units
0	Time Epoch	Seconds
1	Wind Lull (minimum 3 second sample)	m/s
2	Wind Avg (average over report interval)	m/s
3	Wind Gust (maximum 3 second sample)	m/s
4	Wind Direction	Degrees
5	Wind Sample Interval	seconds
6	Station Pressure	MB
7	Air Temperature	C
8	Relative Humidity	%
9	Illuminance	Lux
10	UV	Index
11	Solar Radiation	W/m^2
12	Precip Accumulated	mm
13	Precipitation Type	0 = none, 1 = rain, 2 = hail
14	Lightning Strike Avg Distance	km
15	Lightning Strike Count	
16	Battery	Volts
17	Report Interval	Minutes

obs_sky
Index	Field	Units
0	Time Epoch	Seconds
1	Illuminance	Lux
2	UV	Index
3	Rain Accumulated	mm
4	Wind Lull (minimum 3 second sample)	m/s
5	Wind Avg (average over report interval)	m/s
6	Wind Gust (maximum 3 second sample)	m/s
7	Wind Direction	Degrees
8	Battery	Volts
9	Report Interval	Minutes
10	Solar Radiation	W/m^2
11	Local Day Rain Accumulation	mm
12	Precipitation Type	0 = none, 1 = rain, 2 = hail
13	Wind Sample Interval	seconds

obs_air
Index	Field	Units
0	Time Epoch	Seconds
1	Station Pressure	MB
2	Air Temperature	C
3	Relative Humidity	%
4	Lightning Strike Count	
5	Lightning Strike Avg Distance	km
6	Battery	
7	Report Interval	Minutes

------------------------------
evt_strike evt data format
Index	Field	Units
0	Time Epoch	Seconds
1	Distance	km
2	Energy	

------------------------------
device_status sensor_status values
Sensor Status (sensor_status) is a set of bit flags, encoded in a single decimal value, each bit represents the following
Binary Value	Applies to device	Status description
0b000000000	All	Sensors OK
0b000000001	AIR, Tempest	lightning failed
0b000000010	AIR, Tempest	lightning noise
0b000000100	AIR, Tempest	lightning disturber
0b000001000	AIR, Tempest	pressure failed
0b000010000	AIR, Tempest	temperature failed
0b000100000	AIR, Tempest	rh failed
0b001000000	SKY, Tempest	wind failed
0b010000000	SKY, Tempest	precip failed
0b100000000	SKY, Tempest	light/uv failed

------------------------------
device_status debug values
Value	Description
0	Debugging is disabled
1	Debugging is enabled

------------------------------
hub_status reset_flags values
Value	Description
BOR	Brownout reset
PIN	PIN reset
POR	Power reset
SFT	Software reset
WDG	Watchdog reset
WWD	Window watchdog reset
LPW	Low-power reset

------------------------------
hub_status radio_stats values
0	Version
1	Reboot Count
2	I2C Bus Error Count
3	Radio Status (0 = Radio Off, 1 = Radio On, 3 = Radio Active)
4	Radio Network ID
"""

# Define what type of data various field names have, used for determining how to convert data to current locale
FIELD_TYPES = { 'timestamp': 'epoch',
                'wind_lull': 'speed',
                'barometric_pressure': 'pressure',
                'air_temperature': 'temperature' }


def add_data_keys(data, api_type=None):
    """
    Convert fields within data from integer arrays to dictionaries using defined data formats
    :param data: Data to convert fields within
    :param api: API type to obtain data format for (rest, websocket, udp)
    :return: Data with fields converted
    """
    # Set data format based on API used
    if api_type == 'rest':
        api_data_format = REST_DATA_FORMAT
    elif api_type == 'websocket':
        api_data_format = WS_DATA_FORMAT
    elif api_type == 'udp':
        api_data_format = UDP_DATA_FORMAT
    else:
        return data

    # If data has no type or we have no conversion for type then we have no idea how to convert
    if 'type' not in data or data['type'] not in api_data_format:
        return data

    # Loop all fields in data
    data_type = data['type']
    for data_field in data:
        # If we have conversion for this data type's field then convert field value to dictionary
        if data_field in api_data_format[data_type]:
            value_names = api_data_format[data_type][data_field]

            # If data field is single value, convert as normal, otherwise convert all values
            if type(data[data_field][0]) != list:
                data[data_field] = convert_list(data[data_field], value_names)
            else:
                for i, val in enumerate(data[data_field]):
                    data[data_field][i] = convert_list(data[data_field][i], value_names)

    return data


def convert_list(data, value_names):
    """
    Convert a list of numbers to a dictionary with keys defining values
    :param data: List to convert
    :param value_names: List of names to use as keys for each value in the array
    :return: Dictionary containing values with keys defining values
    """
    new_data = {}
    for i, key in enumerate(value_names):
        new_data[key] = data[i]

    return new_data
