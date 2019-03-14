
from dnac import Dnac
from dnac.networkdevice import NetworkDevice

MODULE = 'networkdevice_example.py'

print('%s: setting up Cisco DNA Center and its API...' % MODULE)
dnac = Dnac()
ndapi = NetworkDevice(dnac, 'devices')

print('%s: getting all devices...' % MODULE)
# The handle 'ndapi' could be used here, but the point of this example is
# demonstrate how to get it directly from the Dnac.api{} using the API's name.
devices = dnac.api['devices'].get_all_devices()

print('%s: found the following devices:' % MODULE)
for device in devices:
    print('hostname: %s\tserial: %s\tIP: %s' %
          (device['hostname'], device['serialNumber'],
           device['managementIpAddress']))
print()
