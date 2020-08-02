"""
Valid returned data types:
    evt_precip
    evt_strike
    rapid_wind
    obs_air
    obs_sky
    obs_st

    ack
    evt_station_online
    evt_station_offline
"""
class Websocket:
    def __init__(self):
        self.datasource = 'websocket'
