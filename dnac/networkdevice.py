
from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS
from dnac.timestamp import TimeStamp

MODULE = 'networkdevice.py'

NETWORK_DEVICE_RESOURCE_PATH = {
    '1.2.8': '/dna/intent/api/v1/network-device',
    '1.2.10': '/dna/intent/api/v1/network-device'
}

DEVICE_DETAIL_RESOURCE_PATH = {
    '1.2.10': '/dna/intent/api/v1/device-detail'
}

DEVICE_DETAIL_IDENTIFIERS = {
    'mac': 'macAddress',
    'id': 'uuid',
    'name': 'nwDeviceName'
}

# error messages
NO_DEVICES = 'API response list is empty'
CHECK_HOSTNAME = 'Check the hostname'
CHECK_IP = 'Check the management IP address'
CHECK_REGEX = 'Check the regular expression'


class NetworkDevice(DnacApi):
    """
    The NetworkDevice class wraps Cisco's DNA Center network-device API
    calls.  It inherits from class DnacApi for its attributes, and in its
    current form, it does not extend these attributes with any others.
    NetworkDevice does, however, provide a set of functions that handle
    the details behind the API's various permutations.  Use this API
    to retrieve information about network equipment under Cisco DNAC's
    management.

    NetworkDevice automatically sets the resource path for the network-
    device API call based upon the version of Cisco DNA Center indicated
    in the Dnac object.  Edit the configuration file dnac_config.py and
    set DNAC_VERSION to the version of Cisco DNA Center being used.

    To use this class, instantiate a new object with a pointer to a Dnac
    object and a name for the NetworkDevice object used to access it
    in a Dnac object's API store (Dnac.api{}).  To make API calls with it,
    reference it from the API store and execute one of its functions.

    Attributes:
        dnac:
            Dnac object: A reference to the Dnac instance that contains
                         a NetworkDevice object
            default: none
            scope: protected
        name:
            str: A user friendly name for the NetworkDevice object and is
                 used as a key for finding it in a Dnac.api attribute.
            default: none
            scope: protected
        devices:
            list or dict: The results returned by making an API call.
            default: none
            scope: protected
        device_detail:
            dict: A device's detailed configuration, state and health.
            default: {}
            scope: protected
        vlans:
            list: The results returned when making an API call that
                  specifically asks for VLAN information from a device.
            default: []
            scope: protected
        verify: Flag indicating whether or not the request should verify
                Cisco DNAC's certificate.
            type: boolean
            default: False
            scope: protected
        timeout: The number of seconds the request for a token should wait
                 before assuming Cisco DNAC is unavailable.
            type: int
            default: 5
            scope: protected

    Usage:
        d = Dnac()
        nd = NetworkDevice(d, 'network-device')
        d.api[nd.name] = nd
        devices = d.api['network-device'].get_all_devices()
        for device in devices:
            pprint.PrettyPrint(device['hostname'])
    """
    def __init__(self,
                 dnac,
                 name,
                 verify=False,
                 timeout=5):
        """
        The __init__ class method instantiates a new NetworkDevice object.
        Be certain that a Dnac object is first created, then pass that
        object and a user-friendly name for the NetworkDevice instance
        that can be used to access it in the Dnac.api dictionary.

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: none
                required: Yes
            name: A user friendly name for find this object in a Dnac
                  instance.
                type: str
                default: none
                required: yes
            verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: no
            timeout: The number of seconds to wait for Cisco DNAC's
                     response.
                type: int
                default: 5
                required: no

        Return Values:
            NetworkDevice object: a new NetworkDevice object.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
        """
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = NETWORK_DEVICE_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError(
                '__init__: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                           )
        if dnac.version in DEVICE_DETAIL_RESOURCE_PATH:
            self.__detail_resource = DEVICE_DETAIL_RESOURCE_PATH[dnac.version]
        else:
            self.__detail_resource = None
        self.__devices = None  # API returns list or dict based on the call
        self.__vlans = []
        self.__device_detail = {}
        super(NetworkDevice, self).__init__(dnac,
                                            name,
                                            resource=path,
                                            verify=verify,
                                            timeout=timeout)

# end __init__()

    def get_all_devices(self):
        """
        The get_all_devices method returns every network device managed
        by Cisco DNA Center.

        Parameters:
            none

        Return Values:
            list: A list of dictionaries.  Each dictionary contains the
                  attributes of a single device managed by Cisco DNAC.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            d.api[nd.name] = nd
            devices = d.api['network-device'].get_all_devices()
            for device in devices:
                pprint.PrettyPrint(device['hostname'])
        """
        url = self.dnac.url + self.resource
        devices, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_all_devices', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(devices)
                              )
        self.__devices = devices['response']
        return self.__devices

# end get_all_devices()

    def get_device_by_id(self, id):
        """
        get_device_by_id finds a device in Cisco DNAC using its UUID.

        Parameters:
            id : str
                default: none
                required: yes

        Return Values:
            list: A list with a single dictionary for the UUID requested.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            d.api[nd.name] = nd
            uuid = '84e4b133-2668-4705-8163-5694c84e78fb'
            device = d.api['network-device'].get_device_by_id(uuid)
            pprint.PrettyPrint(device)
        """

        url = self.dnac.url + self.resource + ('/%s' % id)
        devices, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_device_by_id', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(devices)
                              )
        self.__devices = devices['response']
        return self.__devices

# end det_device_by_id()

    def get_device_by_name(self, name):
        """
        get_device_by_name finds a device in Cisco DNAC using its hostname.

        Parameters:
            name : str
                default: none
                required: yes

        Return Values:
            list: A list with a single dictionary for the host requested.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            d.api[nd.name] =  nd
            name = 'DC1-A3850.cisco.com'
            device = d.api['network-device'].get_device_by_name(name)
            pprint.PrettyPrint(device)
        """
        host_filter = '?hostname=' + name
        url = self.dnac.url + self.resource + host_filter
        devices, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_device_by_name', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(devices)
                              )
        if not devices['response']:  # device list is empty
            raise DnacApiError(
                MODULE, 'get_device_by_name', NO_DEVICES, url,
                '', str(devices['response']), '', CHECK_HOSTNAME
                              )
        self.__devices = devices['response'][0]
        return self.__devices

# end get_device_by_name()

    def get_devices_by_name_with_regex(self, regex):
        """
        The get_devices_by_name_with_regex searches through Cisco DNA Center's
        inventory for all devices whose hostname matches the regular expression
        it is given.

        Parameters:
            regex: str
                default: None
                required: yes

        Return Values:
            list: The devices found according to the regular expression search.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            d.api[nd.name] =  nd
            regex = '.*9300-switch.*'
            devices = d.api['network-device'].get_devices_by_name_with_regex(regex)
            pprint.PrettyPrint(devices)
        """
        host_filter = '?hostname=' + regex
        url = self.dnac.url + self.resource + host_filter
        devices, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_devices_by_name_with_regex(', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(devices)
            )
        if not devices['response']:  # device list is empty
            raise DnacApiError(
                MODULE, 'get_devices_by_name_with_regex(', NO_DEVICES, url,
                '', str(devices['response']), '', CHECK_REGEX
            )
        self.__devices = devices['response']
        return self.__devices

# end get_device_by_name_with_regex

    def get_id_by_device_name(self, name):
        """
        Method get_id_by_device_name finds a device in Cisco DNA Center by
        its hostname and returns its UUID.

        Parameters:
            name: str
                default: none
                required: yes

        Return Values:
            str: The device's UUID in Cisco DNAC.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            id = d.api['network-device'].get_id_by_device_name('R1')
            print id
        """
        device = self.get_id_by_device_name(name)
        return device['id']

# end get_id_by_device_name()

    def get_device_by_ip(self, ip):
        """
        get_device_by_ip finds a device in Cisco DNAC using its managed IP
        address.

        Parameters:
            ip : str
                default: none
                required: yes

        Return Values:
            list: A list with a single dictionary for the requested IP.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            ip = '10.255.1.10'
            device = d.api['network-device'].get_device_by_ip(ip)
            print str(device)
        """
        url = self.dnac.url + self.resource + \
            ('?managementIpAddress=%s' % ip)
        devices, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_device_by_ip', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(devices)
                              )
        if not devices['response']:  # device list is empty
            raise DnacApiError(
                MODULE, 'get_device_by_ip', NO_DEVICES, url,
                '', str(devices['response']), '', CHECK_IP
                              )
        self.__devices = devices['response'][0]
        return self.__devices

# end get_device_by_ip()

    def get_devices_by_ip_with_regex(self, regex):
        """
        The get_devices_by_ip_with_regex searches through Cisco DNA Center's
        inventory for all devices whose management IP address matches the
        regular expression passed.

        Parameters:
            regex: str
                default: None
                required: yes

        Return Values:
            list: The devices found according to the regular expression search.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            d.api[nd.name] =  nd
            regex = '192.168.*.*'
            devices = d.api['network-device'].get_devices_by_ip_with_regex(regex)
            pprint.PrettyPrint(devices)
        """
        url = self.dnac.url + self.resource + \
              ('?managementIpAddress=%s' % regex)
        devices, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_devices_by_ip_with_regex', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(devices)
            )
        if not devices['response']:  # device list is empty
            raise DnacApiError(
                MODULE, 'get_devices_by_ip_with_regex', NO_DEVICES, url,
                '', str(devices['response']), '', CHECK_REGEX
            )
        self.__devices = devices['response']
        return self.__devices


# end get_devices_by_ip_with_regex()

    def get_vlans_by_device_id(self, id):
        """
        get_vlans_by_device_id obtains the list of VLANs configured on the
        device given by its UUID.

        Parameters:
            id : str
                default: none
                required: yes

        Return Values:
            list: The list of VLANs on the network device.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            id = 'a0116157-3a02-4b8d-ad89-45f45ecad5da'
            vlans = d.api['network-device'].get_vlans_by_device_id(id)
            print str(vlans)
        """
        url = self.dnac.url + self.resource + ('/%s/l2vlan' % id)
        vlans, status = self.crud.get(url,
                                      headers=self.dnac.hdrs,
                                      verify=self.verify,
                                      timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_vlans_by_device_id', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(vlans)
                              )
        self.__vlans = vlans['response']
        return self.__vlans

# end get_vlans_by_device_id()

    def get_vlans_by_device_name(self, name):
        """
        get_vlans_by_device_name obtains the list of VLANs configured on the
        device given by its hostname.

        Parameters:
            name : str
                default: none
                required: yes

        Return Values:
            list: The list of VLANs on the network device.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            name = 'S1'
            vlans = d.api['network-device'].get_vlans_by_device_name(name)
            pprint.PrettyPrint(vlans)
        """
        device = self.get_device_by_name(name)
        url = self.dnac.url + self.resource + \
            ('/%s/l2vlan' % device['id'])
        vlans, status = self.crud.get(url,
                                      headers=self.dnac.hdrs,
                                      verify=self.verify,
                                      timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_vlans_by_device_name', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(vlans)
                              )
        self.__vlans = vlans['response']
        return self.__vlans

# end get_vlans_by_device_name()

    def get_vlans_by_device_ip(self, ip):
        """
        get_vlans_by_device_ip obtains the list of VLANs configured on the
        device given its IP address.

        Parameters:
            ip : str
                default: none
                required: yes

        Return Values:
            list: The list of VLANs on the network device.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            ip = '10.255.1.10'
            vlans = d.api['network-device'].get_vlans_by_device_ip(ip)
            pprint.PrettyPrint(vlans)
        """
        device = self.get_device_by_ip(ip)
        url = self.dnac.url + self.resource + \
            ('/%s/l2vlan' % device['id'])
        vlans, status = self.crud.get(url,
                                      headers=self.dnac.hdrs,
                                      verify=self.verify,
                                      timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_vlans_by_device_ip', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(vlans)
                              )
        self.__vlans = vlans['response']
        return self.__vlans

# end get_vlans_by_device_ip()

    def get_device_detail_by_name(self, name):
        """
        get_device_detail_by_name searches for a devices using its hostname
        and returns a detailed listing of its current configuration state
        and health.

        Parameters:
            name: str
                default: None
                required: yes

        Return Values:
            dict: A dictionary of the device's current state

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            hostname = 'c9407.cisco.com'
            details = d.api['network-device'].get_device_detail_by_name(hostname)
            pprint.PrettyPrint(details)
        """
        if not self.__detail_resource:
            raise DnacError(
                'get_device_detail_by_name: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, self.dnac.version)
            )
        time = TimeStamp()
        query = '?timestamp=%s&searchBy=%s&identifier=%s' % \
                (time, name, DEVICE_DETAIL_IDENTIFIERS['name'])
        url = self.dnac.url + self.__detail_resource + query
        detail, status = self.crud.get(url,
                                       headers=self.dnac.hdrs,
                                       verify=self.verify,
                                       timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_device_detail_by_name', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(detail)
            )
        self.__device_detail = detail['response']
        return self.__device_detail

# end get_device_detail_by_name()

    def get_device_detail_by_id(self, id):
        """
        get_device_detail_by_id searches for a devices using its uuid
        and returns a detailed listing of its current configuration state
        and health.

        Parameters:
            id: str
                default: None
                required: yes

        Return Values:
            dict: A dictionary of the device's current state

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            uuid = '84e4b133-2668-4705-8163-5694c84e78fb'
            details = d.api['network-device'].get_device_detail_by_id(uuid)
            pprint.PrettyPrint(details)
        """
        if not self.__detail_resource:
            raise DnacError(
                'get_device_detail_by_id: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, self.dnac.version)
            )
        time = TimeStamp()
        query = '?timestamp=%s&searchBy=%s&identifier=%s' % \
                (time, id, DEVICE_DETAIL_IDENTIFIERS['id'])
        url = self.dnac.url + self.__detail_resource + query
        detail, status = self.crud.get(url,
                                       headers=self.dnac.hdrs,
                                       verify=self.verify,
                                       timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_device_detail_by_id', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(detail)
            )
        self.__device_detail = detail['response']
        return self.__device_detail

# end get_device_detail_by_id()

    def get_device_detail_by_mac(self, mac):
        """
        get_device_detail_by_mac searches for a devices using its MAC address
        and returns a detailed listing of its current configuration state
        and health.

        Parameters:
            mac: str
                default: None
                required: yes

        Return Values:
            dict: A dictionary of the device's current state

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, 'network-device')
            mac = 'DE:AD:BE:EF:01:02'
            details = d.api['network-device'].get_device_detail_by_mac(mac)
            pprint.PrettyPrint(details)
        """
        if not self.__detail_resource:
            raise DnacError(
                'get_device_detail_by_mac: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, self.dnac.version)
            )
        time = TimeStamp()
        query = '?timestamp=%s&searchBy=%s&identifier=%s' % \
                (time, mac, DEVICE_DETAIL_IDENTIFIERS['mac'])
        url = self.dnac.url + self.__detail_resource + query
        detail, status = self.crud.get(url,
                                       headers=self.dnac.hdrs,
                                       verify=self.verify,
                                       timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_device_detail_by_mac', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(detail)
            )
        self.__device_detail = detail['response']
        return self.__device_detail

# end get_device_detail_by_mac()

# end class NetworkDevice()

# begin unit test


if __name__ == '__main__':

    from dnac import Dnac
    import pprint

    pp = pprint.PrettyPrinter(indent=4)
    d = Dnac()
    ndName = 'network-device'
    nd = NetworkDevice(d, ndName)

    print('Network Device:')
    print()
    print('  dnac     = ' + str(type(nd.dnac)))
    print('  name     = ' + nd.name)
    print('  resource = ' + nd.resource)
    print('  verify   = ' + str(nd.verify))
    print('  timeout  = ' + str(nd.timeout))
    print()
    print('Getting all network devices from Cisco DNAC...')

    devs = nd.get_all_devices()

    print()
    print('  devs = ' + str(type(devs)))
    print('  devs = ')
    pp.pprint(devs)
    print()
    print('Getting a network device by its UUID...')
    
    uuid = devs[0]['id']
    print('  id = ' + uuid)
    devs = nd.get_device_by_id(uuid)

    print()
    print('  devs = ')
    pp.pprint(devs)
    print()
    print('Getting network device DC1-A3850.cisco.com by name...')

    devs = nd.get_device_by_name('DC1-A3850.cisco.com')

    print()
    print('  devs = ')
    pp.pprint(devs)
    print()

    print('Getting network device DC1-A3850.cisco.com by IP...')

    devs = nd.get_device_by_ip('10.255.1.10')

    print()
    print('  devs = ')
    pp.pprint(devs)
    print()

    print('Getting device\'s VLANs by its UUID...')
    
    uuid = devs['id']
    print('  id = ' + uuid)
    vlans = nd.get_vlans_by_device_id(uuid)

    print()
    print('  vlans = ')
    pp.pprint(vlans)
    print()
    print('Getting device DC1-A3850.cisco.com\'s VLANs by its name...')

    vlans = nd.get_vlans_by_device_name('DC1-A3850.cisco.com')

    print()
    print('  vlans = ')
    pp.pprint(vlans)
    print()
    print('Getting device VLANs by its IP...')

    vlans = nd.get_vlans_by_device_ip('10.255.1.10')

    print('  vlans = ')
    pp.pprint(vlans)

    print()
    print('Getting device detail by name for DC1-A3850.cisco.com...')
    print()

    detail = nd.get_device_detail_by_name('DC1-A3850.cisco.com')
    pp.pprint(detail)

    print()
    print('Getting device detail by id for %s...' % uuid)
    print()

    detail = nd.get_device_detail_by_id(uuid)
    pp.pprint(detail)

    print()
    print('Getting device detail by mac for 20:37:06:CF:C5:00...')
    print()

    detail = nd.get_device_detail_by_mac('20:37:06:CF:C5:00')
    pp.pprint(detail)

    print()
    print('Getting devices by name with regex .*dc2.* ...')
    print()

    devices = nd.get_devices_by_name_with_regex('.*dc2.*')
    pp.pprint(devices)

    print()
    print('Getting devices by ip with regex 10.255.*.* ...')
    print()

    devices = nd.get_devices_by_ip_with_regex('10.255.*.*')
    pp.pprint(devices)

    print()
    print('NetworkDevice: unit test complete.')
    print()
