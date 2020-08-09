from socket import *
import threading, time, json
from .data import add_data_keys

# Define valid data types to document API and so calling application can be aware if needed
VALID_DATA_TYPES = ('evt_precip', 'evt_strike', 'rapid_wind', 'obs_air', 'obs_sky', 'obs_st', 'device_status',
                    'hub_status')

# Define UDP API parameters
_UDP_VERSION = 143
_UDP_PORT = 50222


class Udp:
    _thread_name = 'weatherflow-udp-listener'
    def __init__(self, bind_address='', debug=False):
        """
        This class utilizes the local UDP broadcast data from the WeatherFlow hub which must exist on the same network
        :param bind_address: IP address of interface to listen on (default is all)
        :param debug: Enable debugging for low-level troubleshooting
        """
        self.debug = debug
        if debug:
            print("Constructing UDP class")

        self.sock = None
        self.start(bind_address)

    def start(self, bind_address='', udp_port=_UDP_PORT):
        """
        Opens the network socket and starts the listening thread, called automatically during construction
        :param bind_address: IP address of interface to listen on (default is all)
        :param udp_port: UDP port to listen on
        :return: Nothing
        """
        # Make sure someone does not try to start the listener twice
        if self.sock:
            if self.debug:
                print("Udp class has already been told to start listening")
        else:
            # Open socket
            try:
                if self.debug:
                    print("Opening UDP listener socket")
                self.sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
                self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                self.sock.setblocking(True)
                self.sock.bind((bind_address, udp_port))
                if self.debug:
                    print("UDP listener socket opened")
            except:
                raise UdpError("Issue listening on socket for UDP broadcast traffic")

            # Latest data will be dict of object types containing dict with keys data, timestamp, fetched
            self.latest_data = {}

            # Start listening
            self.run_thread = True
            self.thread_exception = None
            self.listen_thread = threading.Thread(target=self._listen, name=self._thread_name, daemon=True)

            if self.debug:
                print("Starting thread %s" % self._thread_name)
            self.listen_thread.start()

    def __del__(self):
        """
        We try to call stop automatically, but the calling code should always do this for proper cleanup
        :return:
        """
        self.stop()

    def stop(self):
        """
        Triggers the listening thread to stop and closes the socket
        :return:
        """
        if self.debug:
            print("Triggering %s thread to stop running" % self._thread_name)
        self.run_thread = False

        # Block until the listening thread has stopped running
        while self.listen_thread.is_alive():
            if self.debug:
                print("Waiting for %s thread to shutdown" % self._thread_name)
            time.sleep(.1)

        # If socket not closed yet then close it
        if self.sock:
            if self.debug:
                print("Closing listening socket")
            self.sock.shutdown(SHUT_RDWR)
            self.sock.close()
            self.sock = None

    def _listen(self):
        """
        Method used for creating new thread to listen for incoming data on open socket
        :return:
        """
        if self.debug:
            print("Listener thread %s started" % self._thread_name)

        while self.run_thread:
            if self.debug:
                print("(%s) Listening for data..." % self._thread_name)

            # Get data and send back to parent object so we can retrieve when we need
            try:
                data, host_info = self.sock.recvfrom(1024)
            except:
                self.thread_exception = UdpError("(%s) Issue receiving data from socket" % self._thread_name)
                raise self.thread_exception

            # Convert received data from bytes to string
            raw_data = data.decode()
            if self.debug:
                print("(%s) Received: %s" % (self._thread_name, raw_data))

            # Store data as structure for its object type
            data = json.loads(raw_data)
            if 'type' in data:
                data_type = data['type']
                self.latest_data[data_type] = {'data': data, 'timestamp': time.time(), 'fetched': False}
                self.latest_data['most_recent'] = data_type

        if self.debug:
            print("Listener thread stopped")

    def new_data_available(self, data_type='most_recent'):
        """
        Is new data available?
        :param data_type: Which object type do we want to see if data is available for (or default to most recent data)
        :return: True if yes, false if no
        """
        # Has listener thread thrown an exception?  If so we need to pass onto main program.
        if self.thread_exception:
            raise self.thread_exception

        # If we want most recent data switch data type to what was most recent
        if data_type == 'most_recent' and data_type in self.latest_data:
            data_type = self.latest_data[data_type]

        # Return if data has not been fetched, otherwise we have no data just return False
        if data_type in self.latest_data:
            return not self.latest_data[data_type]['fetched']
        else:
            return False

    def get_latest_data(self, data_type='most_recent', auto_add_data_keys=True):
        """
        Return latest data as regular Python structured and record that latest data has been fetched
        :param data_type: Which object type do we want to see if data is available for (or default to most recent data)
        :param auto_add_data_keys: If true, data arrays will be converted from integer arrays to dictionaries
        :return: Latest data as Python structure (or None if there is no data yet)
        """
        # If we want most recent data switch data type to what was most recent
        if data_type == 'most_recent' and data_type in self.latest_data:
            data_type = self.latest_data[data_type]

        # Return data, otherwise we have no data just return None
        if data_type in self.latest_data:
            self.latest_data[data_type]['fetched'] = True
            if auto_add_data_keys:
                return add_data_keys(self.latest_data[data_type]['data'], 'udp')
            else:
                return self.latest_data[data_type]['data']
        else:
            return None


class UdpError(Exception):
    pass
