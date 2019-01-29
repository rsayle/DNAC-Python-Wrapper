#!/usr/bin/env python

from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnacapi import DnacApi, \
                    DnacApiError
from crud import OK, \
                 REQUEST_NOT_OK, \
                 ERROR_MSGS

MODULE="networkdevice.py"

# error messages
NO_DEVICES="API response list is empty"
CHECK_HOSTNAME="Check the hostname"

class NetworkDevice(DnacApi):
    '''
    The NetworkDevice class wraps Cisco's DNA Center network-device API
    calls.  It inherits from class DnacApi for its attributes, and in its
    current form, it does not extend these attributes with any others.
    NetworkDevice does, however, provide a set of functions that handle
    the details behind the API's various permutations.  Use this API
    to retrieve information about network equipment under Cisco DNAC"s
    management.

    NetworkDevice automatically sets the resource path for the network-
    device API call based upon the version of Cisco DNA Center indicated
    in the Dnac object.  Edit the configuration file dnac_config.py and
    set DNAC_VERSION to the version of Cisco DNA Center being used.

    To use this class, instantiate a new object with a name and place it
    in a Dnac object's API store (Dnac.api{}).  To make API calls with it,
    reference it from the API store and execute one of its functions.

    Cisco DNA Center responds with a dictionary whose first attribute,
    'response', leads to the desired data in the form of a list.
    NetworkDevice's methods simplify processing a response by stripping
    the initial dict and returning the data listing.

    Usage:
        d = Dnac()
        nd = NetworkDevice(d, "network-device")
        d.api[nd.name] = nd
        devices = d.api['network-device'].getAllDevices()
        for device in devices:
            print device['hostname']
    '''

    def __init__(self,
                 dnac,
                 name,
                 verify=False,
                 timeout=5):
        '''
        The __init__ class method instantiates a new NetworkDevice object.
        Be ceratin that a Dnac object is first created, then pass that
        object and a user-friendly name for the NetworkDevice instance
        that can be used to access it in the Dnac.api dictionary.

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: None
                required: Yes
            name: A user friendly name for find this object in a Dnac
                  instance.
                type: str
                default: None
                required: Yes
            verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: No
            timeout: The number of seconds to wait for Cisco DNAC's
                     response.
                type: int
                default: 5
                required: No
        Return Values:
            NetworkDevice object: a new NetworkDevice object.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, "network-device")
        '''

        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = "/dna/intent/api/v1/network-device"
        else:
            raise DnacError(
                "__init__: %s: %s" %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                           )
        self.__devices = None # API returns list or dict based on the call
        self.__vlans = []
        super(NetworkDevice, self).__init__(dnac,
                                            name,
                                            resource=path,
                                            verify=verify,
                                            timeout=timeout)

## end __init__()

    def getAllDevices(self):
        '''
        The getAllDevices method returns every network device managed
        by Cisco DNA Center.

        Parameters:
            None

        Return Values:
            list: A list of dictionaries.  Each dictionary contains the
                  attributes of a single device managed by Cisco DNAC.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, "network-device")
            d.api[nd.name] = nd
            devices = d.api['network-device'].getAllDevices()
            for device in devices:
                print device['hostname']
        '''
        url = self.dnac.url + self.resource
        devices, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, "getAllDevices", REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(results)
                              )
        self.__devices = devices['response']
        return self.__devices

## end getAllDevices()

    def getDeviceById(self, id):
        '''
        getDeviceById finds a device in Cisco DNAC using its UUID.

        Parameters:
            id : str
                default: None
                Required: Yes

        Return Values:
            list: A list with a single dictionary for the UUID requested.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, "network-device")
            d.api[nd.name] = nd
            uuid = '84e4b133-2668-4705-8163-5694c84e78fb'
            device = d.api['network-device'].getDeviceById(uuid)
            print str(device)
        '''
        url = self.dnac.url + self.resource + ("/%s" % id)
        devices, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, "getDeviceById", REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(results)
                              )
        self.__devices = devices['response']
        return self.__devices

## end getDeviceById()

    def getDeviceByName(self, name):
        '''
        getDeviceByName finds a device in Cisco DNAC using its hostname.

        Parameters:
            name : str
                default: None
                Required: Yes

        Return Values:
            list: A list with a single dictionary for the host requested.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, "network-device")
            d.api[nd.name] =  nd
            name = "DC1-A3850.cisco.com"
            device = d.api['network-device'].getDeviceByName(name)
            print str(device)
        '''
        hostfilter = "?hostname=" + name
        url = self.dnac.url + self.resource + hostfilter
        devices, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, "getDeviceByName", REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(results)
                              )
        if not devices['response']: # device list is empty
            raise DnacApiError(
                MODULE, "getDeviceByName", NO_DEVICES, url,
                "", str(devices['response']), "", CHECK_HOSTNAME
                              )
        self.__devices = devices['response'][0]
        return self.__devices

## end getDeviceByName()

    def getIdByDeviceName(self, name):
        device = self.getDeviceByName(name)
        return device['id']

## end getDeviceIdByName()

    def getDeviceByIp(self, ip):
        '''
        getDeviceByIp finds a device in Cisco DNAC using its managed IP
        address.

        Parameters:
            ip : str
                default: None
                Required: Yes

        Return Values:
            list: A list with a single dictionary for the requested IP.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, "network-device")
            d.api[nd.name] = nd
            ip = "10.255.1.10"
            device = d.api['network-device'].getDeviceByIp(ip)
            print str(device)
        '''
        url = self.dnac.url + self.resource + \
            ("?managementIpAddress=%s" % ip)
        devices, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, "getDeviceByIp", REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(results)
                              )
        self.__devices = devices['response'][0]
        return self.__devices

## end getDeviceByIp()

    def getVlansByDeviceId(self, id):
        url = self.dnac.url + self.resource + ("/%s/l2vlan" % id)
        vlans, status = self.crud.get(url,
                                      headers=self.dnac.hdrs,
                                      verify=self.verify,
                                      timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, "getVlansByDeviceId", REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(vlans)
                              )
        self.__vlans = vlans['response']
        return self.__vlans

## end getVlansByDeviceId()

    def getVlansByDeviceName(self, name):
        device = self.getDeviceByName(name)
        hostfilter = "?hostname=" + name
        url = self.dnac.url + self.resource + \
            ("/%s/l2vlan" % device['id'])
        vlans, status = self.crud.get(url,
                                      headers=self.dnac.hdrs,
                                      verify=self.verify,
                                      timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, "getVlansByDeviceName", REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(vlans)
                              )
        self.__vlans = vlans['response']
        return self.__vlans

## end getVlansByDeviceName()

    def getVlansByDeviceIp(self, ip):
        device = self.getDeviceByIp(ip)
        ipfilter = "?managementIpAddress=" + ip
        url = self.dnac.url + self.resource + \
            ("/%s/l2vlan" % device['id'])
        vlans, status = self.crud.get(url,
                                      headers=self.dnac.hdrs,
                                      verify=self.verify,
                                      timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, "getVlansByDeviceIp", REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(vlans)
                              )
        self.__vlans = vlans['response']
        return self.__vlans

## end getVlansByDeviceIp()

## end class NetworkDevice()

## begin unit test

if __name__ == '__main__':

    from dnac import Dnac
    import urllib3

    d = Dnac()
    ndName = "network-device"
    nd = NetworkDevice(d, ndName)

    print "Network Device:"
    print
    print "  dnac    = " + str(type(nd.dnac))
    print "  name    = " + nd.name
    print "  resource = " + nd.resource
    print "  verify  = " + str(nd.verify)
    print "  timeout = " + str(nd.timeout)
    print
    print "Getting all network devices from Cisco DNAC..."

    devs = nd.getAllDevices()

    print
    print "  devs = " + str(type(devs))
    print "  devs = " + str(devs)
    print
    print "Getting a network device by its UUID..."
    
    uuid = devs[0]['id']
    print "  id = " + uuid
    devs = nd.getDeviceById(uuid)

    print
    print "  devs = " + str(devs)
    print
    print "Getting network device DC1-A3850.cisco.com by name..."

    devs = nd.getDeviceByName("DC1-A3850.cisco.com")

    print
    print "  devs = " + str(devs)
    print

    print "Getting network device DC1-A3850.cisco.com by IP..."

    devs = nd.getDeviceByIp("10.255.1.10")

    print
    print "  devs = " + str(devs)
    print

    print "Getting device's VLANs by its UUID..."
    
    uuid = devs['id']
    print "  id = " + uuid
    vlans = nd.getVlansByDeviceId(uuid)

    print
    print "  vlans = " + str(vlans)
    print
    print "Getting device DC1-A3850.cisco.com's VLANs by its name..."

    vlans = nd.getVlansByDeviceName("DC1-A3850.cisco.com")

    print
    print "  vlans = " + str(vlans)
    print
    print "Getting device VLANs by its IP..."

    vlans = nd.getVlansByDeviceIp("10.255.1.10")

    print "  vlans = " + str(vlans)
    print
    print "NetworkDevice: unit test complete."
    print
