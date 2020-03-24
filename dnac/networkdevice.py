
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
    '1.2.10': '/dna/intent/api/v1/network-device',
    '1.3.0.2': '/api/v1/network-device',
    '1.3.0.3': '/api/v1/network-device',
    '1.3.1.3': '/api/v1/network-device',
    '1.3.1.4': '/api/v1/network-device'
}

DEVICE_DETAIL_RESOURCE_PATH = {
    '1.2.10': '/dna/intent/api/v1/device-detail',
    '1.3.0.2': '/api/v1/device-detail',
    '1.3.0.3': '/api/v1/device-detail',
    '1.3.1.3': '/api/v1/device-detail',
    '1.3.1.4': '/api/v1/device-detail'
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
    The NetworkDevice class wraps Cisco's DNA Center network-device API calls.  It inherits from class DnacApi for its
    attributes, and in its current form, it does not extend these attributes with any others.  NetworkDevice does,
    however, provide a set of functions that handle the details behind the API's various permutations.  Use this API
    to retrieve information about network equipment under Cisco DNAC's management.

    NetworkDevice automatically sets the resource path for the network- device API call based upon the version of Cisco
    DNA Center indicated in the Dnac object.  Edit the configuration file dnac_config.py and set DNAC_VERSION to the
    version of Cisco DNA Center being used.

    To use this class, instantiate a new object with a pointer to a Dnac object and a name for the NetworkDevice object
    used to access it in a Dnac object's API store (Dnac.api{}).  To make API calls with it, reference it from the API
    store and execute one of its functions.

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
        The __init__ class method instantiates a new NetworkDevice object. Be certain that a Dnac object is first
        created, then pass that object and a user-friendly name for the NetworkDevice instance that can be used to
        access it in the Dnac.api dictionary.
        :param dnac: A reference to the containing Dnac object.
            type: Dnac object
            default: none
            required: Yes
        :param name: A user friendly name for find this object in a Dnac instance.
            type: str
            default: none
            required: yes
        :param verify: A flag used to check Cisco DNAC's certificate.
            type: boolean
            default: False
            required: no
        :param timeout: The number of seconds to wait for Cisco DNAC's response.
            type: int
            default: 5
            required: no
        """
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = NETWORK_DEVICE_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError('%s: __init__: %s: %s' % (MODULE, UNSUPPORTED_DNAC_VERSION, dnac.version))
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

    @property
    def devices(self):
        """
        Get method for the device list stored in the NetworkDevice instance
        :return: list
        """
        return self.__devices

    # end devices getter

    @property
    def vlans(self):
        """
        Get method for the VLANs on the device represented by the NetworkDevice object.
        :return: list
        """
        return self.__vlans

    # end vlans getter

    @property
    def device_detail(self):
        """
        Provides the device's details as retrieved from Cisco DNA Center.
        :return: dict
        """
        return self.__device_detail

    # end device_detail getter

    def get_all_devices(self):
        """
        The get_all_devices method returns every network device managed by Cisco DNA Center.
        :return: list of dict
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
        :param id: The network device's UUID.
            type: str
            default: none
            required: yes
        :return: list with a single dict
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
        :param name: The device's hostname.
            type : str
            default: none
            required: yes
        :return: list with a single dict
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
        The get_devices_by_name_with_regex searches through Cisco DNA Center's inventory for all devices whose hostname
        matches the regular expression it is given.
        :param regex: A regular expression to find a device or set of network devices.
            type: str
            default: none
            required: yes
        :return: list of dict
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
        Method get_id_by_device_name finds a device in Cisco DNA Center by its hostname and returns its UUID.
        :param name: The network device's hostname.
            type: str
            default: none
            required: yes
        :return:
        """
        device = self.get_device_by_name(name)
        return device['id']

    # end get_id_by_device_name()

    def get_device_by_ip(self, ip):
        """
        get_device_by_ip finds a device in Cisco DNAC using its managed IP address.
        :param ip: The device's IP address.
            type: str
            default: none
            required: yest
        :return:
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
        The get_devices_by_ip_with_regex searches through Cisco DNA Center's inventory for all devices whose
        management IP address matches the regular expression passed.
        :param regex: A regular expression of the IP addresses to search.
            type: str
            default: none
            required: yes
        :return: list of dict
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
        get_vlans_by_device_id obtains the list of VLANs configured on the device given by its UUID.
        :param id: The target device's UUID.
            type: str
            default: none
            required: yest
        :return: list
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
        get_vlans_by_device_name obtains the list of VLANs configured on the device given by its hostname.
        :param name: The device's hostname.
            type: str
            default: none
            required: yes
        :return: list
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
        get_vlans_by_device_ip obtains the list of VLANs configured on the device given its IP address.
        :param ip: The target device's IP management IP address.
            type: str
            default: none
            required: yest
        :return: list
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
        get_device_detail_by_name searches for a devices using its hostname and returns a detailed listing of its
        current configuration state and health.
        :param name: The network device's hostname.
            type: str
            default: none
            required: yest
        :return: dict
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
        get_device_detail_by_id searches for a devices using its uuid and returns a detailed listing of its current
        configuration state and health.
        :param id: The device's UUID.
            type: str
            default: none
            required: yest
        :return: dict
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
        get_device_detail_by_mac searches for a devices using its MAC address and returns a detailed listing of its
        current configuration state and health.
        :param mac: The network device's MAC address.
            type: str
            default: none
            required: yes
        :return: dict
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

