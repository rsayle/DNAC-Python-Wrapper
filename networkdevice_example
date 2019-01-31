#!/usr/bin/env

from dnac import Dnac
from networkdevice import NetworkDevice


print "example.py setting up Cisco DNA Center and its API..."
dnac = Dnac()
ndapi = NetworkDevice(dnac, 'devices')

print "example.py getting all devices..."
# The handle 'ndapi' could be used here, but the point of this example is
# demonstrate how to get it directly from the Dnac.api{} using the API's
# name.
devices = dnac.api['devices'].getAllDevices()


print "example.py found the following devices:"
for device in devices:
    print "hostname: %s\tserial: %s\tIP: %s" % \
          (device['hostname'], device['serialNumber'], 
           device['managementIpAddress'])

print "example.py done."
