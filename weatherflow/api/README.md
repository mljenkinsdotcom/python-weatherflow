# API
Classes for communicating to the various WeatherFlow APIs

## Security
WeatherFlow can authorize requests using either:
* Access tokens - used for accessing your private stations and public stations
* API key - used for accessing public stations

To obtain an access token visit [WeatherFlow Data Authorizations](https://tempestwx.com/settings/tokens),
sign in as your account, and then create a new token (or utilize an existing one).

## Classes

### Rest
Used to communicate to WeatherFlow API for one time returns of data

Methods:
* `getDeviceObservations`
* `getStationObservation`
* `getStations`
* `getStation`
 

Exceptions:
* `RestError` - Issues from WeatherFlow API
* `UsageError` - Issues due to misuse of Rest class


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