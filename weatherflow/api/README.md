# API
Classes for communicating to the various WeatherFlow APIs

## Security
WeatherFlow can authorize requests using either:
* Access tokens - used for accessing your private stations and public stations
* API key - used for accessing public stations

To obtain an access token visit [WeatherFlow Data Authorizations](https://tempestwx.com/settings/tokens),
sign in as your account, and then create a new token (or utilize an existing one).

## Data
WeatherFlow returns many data types as lists of integers.  To make this data more useful, most methods within
this API will auto convert these lists to dictionaries and assign each value a unique key.  You can disable
this by setting the method parameter `auto_add_data_keys` to `False` where the parameter exists on a function.

By assigning unique keys to all value types, we define which data types all possible key values are.  This allows
us to then know how to convert the data to the locale of the calling application as set by the developer.  It also
allows us to use the data by external applications without these applications needing to know the WeatherFlow data
format.

By auto converting the data by default, it should speed up development utilizing the WeatherFlow APIs since the
data will be self documented.

## Classes

### Rest
Used to communicate to WeatherFlow API for one time returns of data

Methods:
* `getDeviceObservations`
* `getStationObservation`
* `getStations`
* `getStation`
 

Exceptions:
* `RestError` - Issues from WeatherFlow API, for example if the service is down, the api key or access token is
incorrect, etc.
* `UDPError` - Issues with the UDP API, primarily caused by not being able to open the network socket or listen
* `UdpParseError` - Data parsing issues, could be caused by data corruption coming from WeatherFlow APIs.
These errors can be typically safely ignored unless they come in masses, we just ignore this bad data.
* `DataFormatError` - Issues if there are data parsing issues, which could occur if the WeatherFlow API
unexpectedly changes or if there is data corruption in transit 

### Websocket
Used for obtaining real time data from WeatherFlow API


### Udp
Used for accessing local broadcast data from WeatherFlow hub.

The Udp class creates a second thread which opens a network socket for listening for the UDP broadcast data.
This socket stays open as long as the class exists.

Methods:
* `new_data_available` - Has new data been received from UDP broadcasts
* `get_latest_data` - Get latest data that has been received from UDP broadcasts
* `start` - Start listening, called automatically when the class is constructed
* `stop` - Stop listening, you should call this for proper cleanup

Example usage:
```python
testudp = weatherflow.api.Udp()
for i in list(range(15)):
    if testudp.new_data_available():
        data = testudp.get_latest_data()
        print(data)
    time.sleep(1)
testudp.stop()
```

### Oauth
Used to obtain OAuth2 access (bearer) tokens for authorization to remote WeatherFlow APIs

Currently not implemented.