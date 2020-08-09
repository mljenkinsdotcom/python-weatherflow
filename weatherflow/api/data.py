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

UDP_DATA_FORMAT = {'rapid_wind': {'ob': ('timestamp', 'wind_gust', 'wind_direction')},
                   'evt_strike': {'evt': ('timestamp', 'lightning_strike_avg_distance', 'lightning_strike_energy')},
                   'hub_status': {'radio_stats': ('version',
                                                  'reboot_count',
                                                  'i2c_bus_error_count',
                                                  'radio_status',
                                                  'radio_network_id')},
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
                                            'report_interval')},
                   'obs_sky': { 'obs': (    'timestamp',
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
                                            'wind_interval')},
                   'obs_air': { 'obs': (    'timestamp',
                                            'barometric_pressure',
                                            'air_temperature',
                                            'relative_humidity',
                                            'lightning_strike_count',
                                            'lightning_strike_avg_distance',
                                            'battery_volts',
                                            'report_interval')}}


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
    # Ensure data format is correct
    if len(data) != len(value_names):
        raise DataFormatError("Data format for list is incorrect, expected %d values but received %d" %
                              (len(value_names), len(data)))

    new_data = {}
    for i, key in enumerate(value_names):
        new_data[key] = data[i]

    return new_data


class DataFormatError(Exception):
    pass
