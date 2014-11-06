"""
Opens connection with device and gives command to clear records.
"""

import usb.core
import usb.util

# find our device using the pre-determined ids
peak_flow_device = usb.core.find(idVendor=0x04B4, idProduct=0x5500)
# dev = usb.core.find(find_all=True)

# was it found?
if peak_flow_device is None:
    raise ValueError('Device not found')

# set the active configuration. With no arguments, the first
# configuration will be the active one
peak_flow_device.set_configuration()

# get the configuration (this device has only one)
configuration = peak_flow_device.get_active_configuration()
# device also only has one interface
interface = configuration[(0,0)]

# get the endpoint for writing to device
endpoint_out = usb.util.find_descriptor(
    interface,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT)

# get the endpoint for receiving from device
endpoint_in = usb.util.find_descriptor(
    interface,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_IN)

# make sure we have both of these
assert endpoint_out is not None
assert endpoint_in is not None

# see if device is ready to be cleared
endpoint_out.write('\x80\x25\x00\x00\x03')
endpoint_out.write('\x05\x3F\x7B\x04\x02\x7D\x00\x00')

try:
    data = peak_flow_device.read(endpoint_in.bEndpointAddress, endpoint_in.wMaxPacketSize, timeout=1000)
    data_formatted = ''.join([hex(x) for x in data])
    print 'First read: ' + data_formatted
except usb.core.USBError as e:
    print e

# clear device
endpoint_out.write('\x80\x25\x00\x00\x03')
endpoint_out.write('\x03\x2D\x7B\x7d\x60\xAD\x64\xFF')

# confirm clear successful
try:
    data = peak_flow_device.read(endpoint_in.bEndpointAddress, endpoint_in.wMaxPacketSize, timeout=1000)
    data_formatted = ''.join([hex(x) for x in data])
    print 'Second read: ' + data_formatted
except usb.core.USBError as e:
    print e