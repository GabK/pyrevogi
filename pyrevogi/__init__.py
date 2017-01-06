from threading import Lock

from bluetooth.ble import GATTRequester
import logging

class Bulb(object):
    #
    # Commands
    #
    GET_CONFIG = (0x2b, 0x05, 0x04)
    SET_CONFIG = (0x2b, 0x0d, 0x03)
    GET_NAME = (0x03, None, None)
    SET_RESET = (0x2b, 0x05, 0x0b)

    #
    # Color & brightness constants
    #
    MAX_RED = 0xff
    MIN_RED = 0x00
    MAX_GREEN = 0xff
    MIN_GREEN = 0x00
    MAX_BLUE = 0xff
    MIN_BLUE = 0x00
    MAX_BRIGHTNESS = 0xc8
    MIN_BRIGHTNESS = 0x00

    #
    # Bulb statuses
    #
    STATUS_OFF = 0xff
    STATUS_ON = 0xfe

    _requester = None
    _lock = Lock()

    name = None
    _red = MAX_RED
    _green = MAX_GREEN
    _blue = MAX_BLUE
    _brightness = MIN_BRIGHTNESS

    def __init__(self, address):
        self._requester = GATTRequester(address, False)
        self._requester.on_notification = self.on_notification
        self._send_command(self.GET_CONFIG)

    @property
    def state(self):
        return self.brightness != self.STATUS_OFF and self.brightness != self.MIN_BRIGHTNESS

    @state.setter
    def state(self, value):
        if self.state != value:
            if value:
                self._brightness = self.STATUS_ON
            else:
                self._brightness = self.STATUS_OFF
            self._send_command(self.SET_CONFIG)

    @property
    def color(self):
        return "#{0}{1}{2}".format(hex(self._red), hex(self._green), hex(self._blue))

    @color.setter
    def color(self, value):
        if value.startswith('#'):
            value = value[1:]

        value = (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))

        if self.red != value[0] or self.green != value or self.blue != value:
            self._red = max(min(value[0], self.MAX_RED), self.MIN_RED)
            self._green = max(min(value[1], self.MAX_GREEN), self.MIN_GREEN)
            self._blue = max(min(value[2], self.MAX_BLUE), self.MIN_BLUE)
            self._send_command(self.SET_CONFIG)

    @property
    def red(self):
        return self._red

    @red.setter
    def red(self, value):
        if self.red != value:
            self._red = max(min(value, self.MAX_RED), self.MIN_RED)
            self._send_command(self.SET_CONFIG)

    @property
    def green(self):
        return self._green

    @green.setter
    def green(self, value):
        if self.green != value:
            self._green = max(min(value, self.MAX_GREEN), self.MIN_GREEN)
            self._send_command(self.SET_CONFIG)

    @property
    def blue(self):
        return self._blue

    @blue.setter
    def blue(self, value):
        if self.blue != value:
            self._blue = max(min(value, self.MAX_BLUE), self.MIN_BLUE)
            self._send_command(self.SET_CONFIG)

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if self.brightness != value:
            self._brightness = max(min(value, self.MAX_BRIGHTNESS), self.MIN_BRIGHTNESS)
            self._send_command(self.SET_CONFIG)

    def _send_command(self, command):
        self.connect()

        if command == self.GET_NAME:
            self.name = self._requester.read_by_handle(command[0])[0]
        else:
            payload = [0x0f, command[1], command[2], 0x00]

            if command == self.SET_CONFIG:
                payload += [self.red, self.green, self.blue, self.brightness, 0x00, 0x00, 0x00, 0x00]

            checksum = (sum(payload[2:]) + 1) & 0xFF
            payload += [0x00, 0x00, checksum, 0xff, 0xff]
            
            logging.debug("Sending {0} to handle {1}".format(str([hex(i) for i in payload]), hex(command[0])))

            self._requester.write_by_handle(command[0], str(bytearray(payload)))

    def on_notification(self, handle, data):
        response = [int(b.encode("hex"), 16) for b in data]

        # Parse notification for READ command
        if len(response) == 21:
            self._red = response[7]
            self._green = response[8]
            self._blue = response[9]
            self._brightness = response[10]

        self.disconnect()
        self._lock.release()

    def connect(self):
        self._lock.acquire()
        self._requester.connect()

    def disconnect(self):
        self._requester.disconnect()