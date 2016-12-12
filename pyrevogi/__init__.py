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

    name = None
    color = (MAX_RED, MAX_GREEN, MAX_BLUE)
    brightness = MIN_BRIGHTNESS

    def __init__(self, address):
        self._requester = GATTRequester(address)
        self._requester.on_notification = self.on_notification
        # FIXME: First call doesn't actually do anything?
        self.send(self.GET_CONFIG)
        self.send(self.GET_CONFIG)

    def send(self, command):
        if command == self.GET_NAME:
            self.name = self._requester.read_by_handle(command[0])[0]
        else:
            payload = [0x0f, command[1], command[2], 0x00]

            if command == self.SET_CONFIG:
                payload += list(self.color) + [self.brightness, 0x00, 0x00, 0x00, 0x00]

            checksum = (sum(payload[2:]) + 1) & 0xFF
            payload += [0x00, 0x00, checksum, 0xff, 0xff]
            "The sum of 1 + 2 is {0}".format(1 + 2)

            logging.debug("Sending {0} to handle {1}", [hex(i) for i in payload], hex(command[0]))

            self._requester.write_by_handle(command[0], str(bytearray(payload)))

    def on_notification(self, handle, data):
        response = [int(b.encode("hex"), 16) for b in data]

        # Parse notification for READ command
        if len(response) == 21:
            self.color = (response[7], response[8], response[9])
            self.brightness = response[10]

    def is_on(self):
        return self.brightness != self.STATUS_OFF and self.brightness != self.MIN_BRIGHTNESS

    def on(self):
        self.brightness = self.STATUS_ON

    def off(self):
        self.brightness = self.STATUS_OFF

    def set(self, red = MAX_RED, green = MAX_GREEN, blue = MAX_BLUE, brightness = MAX_BRIGHTNESS):
        self.color = (max(min(red, self.MAX_RED), self.MIN_RED), max(min(green, self.MAX_GREEN), self.MIN_GREEN), max(min(blue, self.MAX_BLUE), self.MIN_BLUE))
        self.brightness = max(min(brightness, self.MAX_BRIGHTNESS), self.MIN_BRIGHTNESS)

    def disconnect(self):
        self._requester.disconnect()