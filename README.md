# WeatherFlow Python Library
Python library to help with using [WeatherFlow SmartWeather API](https://weatherflow.github.io/SmartWeather/)

This is a new project I am working on and is in early development.

The intended use is as follows:
* [weatherflow.api](weatherflow/api) - Classes to perform API connections to read data
    * [Rest](weatherflow/api/rest.py)
    * [Udp](weatherflow/api/udp.py)
    * [Websocket](weatherflow/api/websocket.py)
* [weatherflow.data](weatherflow/data) - Classes to process data 

See the [tests](tests) for example usages.