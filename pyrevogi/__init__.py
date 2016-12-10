from bluetooth.ble import GATTRequester
import time

#
# Commands
#
READ = (0x05, 0x04)
WRITE = (0x0d, 0x03)
RESET = (0x05, 0x0b)

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

#
# BLE handles
#
BULB_NAME = 0x03
BULB_CONFIG = 0x2b

class Bulb(object):
    _requester = None

    name = None
    color = (MAX_RED, MAX_GREEN, MAX_BLUE)
    brightness = MIN_BRIGHTNESS

    def __init__(self, address):
        self._requester = GATTRequester(address)
        self._requester.on_notification = self.on_notification
        # FIXME: First call doesn't actually do anything?
        self.send(BULB_CONFIG, READ)
        self.send(BULB_CONFIG, READ)
        #time.sleep(5)
        #self.send(BULB_NAME)

    def send(self, handle, command = None):
        if handle == BULB_NAME:
            self.name = self._requester.read_by_handle(handle)[0]
        elif handle == BULB_CONFIG and command is not None:
            payload = [0x0f] + list(command) + [0x00]

            if command == WRITE:
                payload += list(self.color) + [self.brightness, 0x00, 0x00, 0x00, 0x00]

            #print payload[2:]
            checksum = (sum(payload[2:]) + 1) & 0xFF
            payload += [0x00, 0x00, checksum, 0xff, 0xff]
            #print payload
            self._requester.write_by_handle(handle, str(bytearray(payload)))

    def on_notification(self, handle, data):
        response = [int(b.encode("hex"), 16) for b in data]
        self.color = (response[7], response[8], response[9])
        self.brightness = response[10]

    def is_on(self):
        return self.brightness == STATUS_ON or self.brightness != MIN_BRIGHTNESS

    def on(self):
        self.brightness = STATUS_ON

        self.send(BULB_CONFIG, WRITE)

    def off(self):
        self.brightness = STATUS_OFF

        self.send(BULB_CONFIG, WRITE)

    def reset(self):
        self.send(BULB_CONFIG, RESET)

    def set(self, red = MAX_RED, green = MAX_GREEN, blue = MAX_BLUE, brightness = MAX_BRIGHTNESS):
        self.color = (max(min(red, MAX_RED), MIN_RED), max(min(green, MAX_GREEN), MIN_GREEN), max(min(blue, MAX_BLUE), MIN_BLUE))
        self.brightness = max(min(brightness, MAX_BRIGHTNESS), MIN_BRIGHTNESS)

        self.send(BULB_CONFIG, WRITE)

    def disconnect(self):
        self._requester.disconnect()