#!/usr/bin/env python

from dnac import SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnacapi import DnacApi, \
                    DnacApiError, \
                    REQUEST_NOT_OK
import requests
import json

## exceptions

## errors
NO_DEVICES="No devices found in DNAC"
DEVICE_NOT_FOUND="Could not find the device"

class NetworkDeviceError(DnacApiError):
    def __init__(self, msg):
        super(NetworkDeviceError, self).__init__(msg)

## end exceptions

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
    device API call based upon the version of Cisco DNA Center indicated in
    the Dnac object.  Edit the configuration file dnac_config.py and
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
                 requestFilter="",
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
            requestFilter: An expression for filtering Cisco DNAC's
                           response.  The NetworkDevice methods already
                           set the request filter as necessary to execute
                           their intended function; however, this can be
                           used for customizing calls not delivered in this
                           implementation.
                type: str
                default: None
                required: No
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
            self.__respath = "/dna/intent/api/v1/network-device"
        else:
            raise NetworkDeviceError(
                "__init__: %s: %s" %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                                    )
            # rewrite this to raise an exception
            print "Unsupported version of Cisco DNAC: " + dnac.version

        super(NetworkDevice, self).__init__(dnac,
                                            name,
                                            resourcePath=self.__respath,
                                            requestFilter=requestFilter,
                                            verify=verify,
                                            timeout=timeout)
## end __init__()

    def getNetworkDeviceApi(url, hdrs={}, body={}, filter=""):
        if not hdrs: # empty hdrs - use the object's default
            hdrs = self.hdrs
        resp = requests.request("GET",
                                url, 
                                headers=hdrs,
                                data=body,
                                verify=self.verify,
                                timeout=self.timeout)
        if resp.status_code != requests.codes.ok:
            raise NetworkDeviceError(
                "getNetworkDeviceApi: %s: %s: %s: expected %s" %
                (REQUEST_NOT_OK, url, str(resp.status_code),
                str(requests.codes.ok))
                                    )
        devices = json.loads(resp.text)['response']
        if not devices: # nothing returned from DNAC
            raise NetworkDeviceError(
                "getNetworkDeviceApi: %s " % NO_DEVICES
                                    )
        return devices

## end getNetworkDeviceApi()

    def putNetworkDeviceApi(url, hdrs={}, body={}, filter=""):
        if not hdrs: # empty hdrs - use the object's default
            hdrs = self.hdrs
        resp = requests.request("PUT",
                                url, 
                                headers=hdrs,
                                data=body,
                                verify=self.verify,
                                timeout=self.timeout)
        if resp.status_code != requests.codes.ok:
            raise NetworkDeviceError(
                "putNetworkDeviceApi: %s: %s: %s: expected %s" %
                (REQUEST_NOT_OK, url, str(resp.status_code),
                str(requests.codes.ok))
                                    )
        devices = json.loads(resp.text)['response']
        if not devices: # nothing returned from DNAC
            raise NetworkDeviceError(
                "putNetworkDeviceApi: %s " % NO_DEVICES
                                    )
        return devices

## end putNetworkDeviceApi()

    def postNetworkDeviceApi(url, hdrs={}, body={}, filter=""):
        if not hdrs: # empty hdrs - use the object's default
            hdrs = self.hdrs
        resp = requests.request("POST",
                                url, 
                                headers=hdrs,
                                data=body,
                                verify=self.verify,
                                timeout=self.timeout)
        if resp.status_code != requests.codes.ok:
            raise NetworkDeviceError(
                "postNetworkDeviceApi: %s: %s: %s: expected %s" %
                (REQUEST_NOT_OK, url, str(resp.status_code),
                str(requests.codes.ok))
                                    )
        devices = json.loads(resp.text)['response']
        if not devices: # nothing returned from DNAC
            raise NetworkDeviceError(
                "postNetworkDeviceApi: %s " % NO_DEVICES
                                    )
        return devices

## end postNetworkDeviceApi()

    def deleteNetworkDeviceApi(url, hdrs={}, body={}, filter=""):
        if not hdrs: # empty hdrs - use the object's default
            hdrs = self.hdrs
        resp = requests.request("DELETE",
                                url, 
                                headers=hdrs,
                                data=body,
                                verify=self.verify,
                                timeout=self.timeout)
        if resp.status_code != requests.codes.ok:
            raise NetworkDeviceError(
                "deleteNetworkDeviceApi: %s: %s: %s: expected %s" %
                (REQUEST_NOT_OK, url, str(resp.status_code),
                str(requests.codes.ok))
                                    )
        devices = json.loads(resp.text)['response']
        if not devices: # nothing returned from DNAC
            raise NetworkDeviceError(
                "deleteNetworkDeviceApi: %s " % NO_DEVICES
                                    )
        return devices

## end deleteNetworkDeviceApi()

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
        url = self.dnac.url + self.respath + self.filter
        return self.getNetworkDeviceApi(url)

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
        url = self.dnac.url + self.respath + ("/%s" % id)
        return self.getNetworkDeviceApi(url)

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
        url = self.dnac.url + self.respath
        return self.getNetworkDeviceApi(url, filter=hostfilter)

## end getDeviceByName()

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
        ipfilter = "?managementIpAddress=" + ip
        url = self.dnac.url + self.respath
        return self.getNetworkDeviceApi(url, filter=ipfilter)

## end getDeviceByIp()

    def getVlansByDeviceId(self, id):
        url = self.dnac.url + self.respath + ("/%s/l2vlan" % id)
        return self.getNetworkDeviceApi(url)

## end getVlansByDeviceId()

    def getVlansByDeviceName(self, name):
        device = getDeviceByName(name)
        hostfilter = "?hostname=" + name
        url = self.dnac.url + self.respath + ("/%s/l2vlan" % device['id'])
        return self.getNetworkDeviceApi(url, filter=hostfilter)

## end getVlansByDeviceName()

    def getVlansByDeviceIp(self, ip):
        device = getDeviceByIp(ip)
        ipfilter = "?managementIpAddress=" + ip
        url = self.dnac.url + self.respath + ("/%s/l2vlan" % device['id'])
        return self.getNetworkDeviceApi(url, filter=ipfilter)

## end getVlansByDeviceIp()

## end class NetworkDevice()

## begin unit test

if __name__ == '__main__':

    from dnac import Dnac
    import urllib3

    requests.packages.urllib3.disable_warnings()

    d = Dnac()
    ndName = "network-device"
    nd = NetworkDevice(d, ndName)

    print "Network Device:"
    print
    print "  dnac    = " + str(type(nd.dnac))
    print "  name    = " + nd.name
    print "  respath = " + nd.respath
    print "  filter  = " + nd.filter
    print "  verify  = " + str(nd.verify)
    print "  timeout = " + str(nd.timeout)
    print
    print "Getting all network devices from Cisco DNAC..."

    devs = nd.getAllDevices()

    print
    print "  devs = " + str(type(devs))
    print "  devs = " + str(devs)
    print
    print "Getting network device DC1-A3850.cisco.com with a filter..."

    f="?hostname=DC1-A3850.cisco.com"
    nd.filter = f
    print "  filter = " + nd.filter
    devs = nd.getAllDevices()

    print
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

    def raiseNetworkDeviceError(msg):
        raise NetworkDeviceError(msg)

    errors = (UNSUPPORTED_DNAC_VERSION,
              REQUEST_NOT_OK,
              NO_DEVICES,
              DEVICE_NOT_FOUND)

    for error in errors:
        try:
            raiseNetworkDeviceError(error)
        except NetworkDeviceError, e:
            print str(type(e)) + " = " + str(e)

    print
    print "NetworkDevice: unit test complete."
    print
