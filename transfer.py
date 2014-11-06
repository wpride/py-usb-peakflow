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

        full_read += data_formatted

        collected += 1
    except usb.core.USBError as e:
        print e
        data = None
        break

print "Full read: " + full_read

replaced_read = full_read.replace("0x","")

# 508 369

print "Replaced string: " + replaced_read;

format_type = replaced_read[0:2]

print "Format type: " + format_type

# two possible encoding format types encoded by the first two characters: either f3 or f4
# the components are ordered and demarcated slightly differently.
if format_type=="f3":

    end_index = replaced_read.rfind("7d")
    print("End Index chars: " + replaced_read[end_index:end_index+2])

    first_fev = replaced_read[end_index-2:end_index]
    print("First fev: " + first_fev)

    f4_check = replaced_read[end_index-4:end_index-2]
    print("f4 check: " + f4_check)
    assert f4_check=="f4"

    second_fev = replaced_read[end_index-6:end_index-4]
    print("Second fev: " + second_fev)
    print("FEV: " + first_fev + second_fev)

    first_pf = replaced_read[end_index-8:end_index-6]
    second_pf = replaced_read[end_index-10:end_index-8]
    print("Peak Flow: " + first_pf + second_pf)
elif format_type=="f4":
    end_index = replaced_read.rfind("7d")
    print("End Index chars: " + replaced_read[end_index:end_index+2])
    f3_check = replaced_read[end_index-2:end_index]
    print("f3 check: " + f3_check)
    assert f3_check=="f3"
    first_fev = replaced_read[end_index-4:end_index-2]
    print("First fev: " + first_fev)
    second_fev = replaced_read[end_index-6:end_index-4]
    print("Second fev: " + second_fev)
    print("FEV: " + first_fev + second_fev)
    first_pf = replaced_read[end_index-8:end_index-6]
    second_pf = replaced_read[end_index-10:end_index-8]
    print("Peak Flow: " + first_pf + second_pf)