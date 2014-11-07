"""
Opens connection with device and reads information.
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

# initiate the transfer
endpoint_out.write('\x80\x25\x00\x00\x03')
endpoint_out.write('\x03\x2F\x7B\x7D\xD8\x52\x68\xFF')

collected = 0
attempts = 10

full_read = "";

# attempt to read data attempts times
while collected < attempts:
    try:
        # read data from the input endpoint
        data = peak_flow_device.read(endpoint_in.bEndpointAddress, endpoint_in.wMaxPacketSize, timeout=1000)
        # format the data to be legible as hex
        # we need to use zfill because hex() will remove leading 0's
        # http://stackoverflow.com/questions/15884677/python-printing-hex-removes-first-0

        data_formatted = ''.join([hex(x)[2:].zfill(2) for x in data])

        print data_formatted
        # don't use the first two chars; these are (to our purposes) meaningless
        full_read += data_formatted[2:]

        collected += 1
    except usb.core.USBError as e:
        print e
        data = None
        break

print "Full read: " + full_read

# take out hex prepends
replaced_read = full_read.replace("0x","")
# split along EOL delimiter
split_string = replaced_read.split('7d')[:-1]
# for each delimiter, pull out PF knowing its -8 -> -5 from index
for part in split_string:
    first_pf = part[-8:-6]
    second_pf = part[-5:-4]
    print("Peak Flow : " + second_pf + first_pf)