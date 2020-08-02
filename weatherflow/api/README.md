# API
Classes for communicating to the various WeatherFlow APIs

## Security
WeatherFlow utilizes an implicit grant type for their Swagger implementation but they
do not yet have a self service capability for obtaining access tokens.

Hence, the to obtan an access token currently:
1. Visit [WeatherFlow Swagger documentation page](https://weatherflow.github.io/SmartWeather/api/swagger/)
2. Click the `Authorize` button on the top right
3. Select the `user` scope
4. Click the `Authorize` button
4. Click the `Allow` button
5. Scroll down to Stations and click `Stations`
6. Click `GET /Stations`
7. Scroll down and click `Try it out!`
8. Under the Curl example request, obtain the access token from the `Authorization` header `Bearer` token value 


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