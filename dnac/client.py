
from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS
from dnac.timestamp import TimeStamp

# globals

MODULE = 'client.py'

CLIENT_RESOURCE_PATH = {
    '1.2.10': '/dna/intent/api/v1/client-detail',
    '1.3.0.2': '/dna/intent/api/v1/client-detail',
    '1.3.0.3': '/dna/intent/api/v1/client-detail',
    '1.3.1.3': '/dna/intent/api/v1/client-detail',
    '1.3.1.4': '/dna/intent/api/v1/client-detail'
}

NULL_MAC = '00:00:00:00:00:00'
BCAST_MAC = 'FF:FF:FF:FF:FF:FF'
ILLEGAL_MAC_ADDRS = [
    NULL_MAC,
    BCAST_MAC
]

# error messages
ILLEGAL_MAC = 'Illegal MAC address'
SET_CLIENT_MAC = 'Set the client\'s MAC address to a legal value'
CLIENT_NOT_FOUND = 'Requested client could not be found'

class Client(DnacApi):
    """
    The Client class represents a host or end-point as represented in Cisco DNA Center.
    In this API's current form, client's can only be searched using their MAC address.
    Once located, the API returns the client's state according to a given time stamp.  At
    the moment, this class pulls the client's state for the current time only.

    Attributes:
        dnac: A reference to the Dnac instance that contains a Client object
            type: Dnac object
            default: none
            scope: protected
        name: A user friendly name for the Client object used as a key for finding it in a Dnac.api attribute.
            type: str
            default: none
            scope: protected
        mac: The end-point's MAC address
            type: str
            default: 00:00:00:00:00:00
            scope: public
        client_detail: The host's current state
            type: dict
            scope: protected
        verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: no
        timeout: The number of seconds to wait for Cisco DNAC's
                 response.
            type: int
            default: 5
            required: no

    Usage:
        d = Dnac()
        host = Client(d, 'myPC', mac='a1:b2:c3:d4:e5:f6')
    """

    def __init__(self,
                 dnac,
                 name,
                 mac=NULL_MAC,
                 verify=False,
                 timeout=5):
        """
        Creates a new client object.
        :param dnac: A reference to the program's Dnac instance.
            type: Dnac object
            required: yes
            default: None
        :param name: The client's name.
            type: str
            required: yes
            default: None
        :param mac: The client's MAC address
            type: str
            required: no
            default: NULL_MAC (00:00:00:00:00:00)
        :param verify: A flag to determine whether or not to verify Cisco DNA Center's certificate.
            type: bool
            required: no
            default: False
        :param timeout: The time in seconds to wait for Cisco DNAC's response.
            type: int
            required: no
            default: 5
        """
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = CLIENT_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError(
                '__init__: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                           )
        self.__mac = mac
        self.__client_detail = {}
        super(Client, self).__init__(dnac,
                                     name,
                                     resource=path,
                                     verify=verify,
                                     timeout=timeout)

    # end __init__()

    @property
    def mac(self):
        """
        Get method mac return's the Client's assigned MAC address.
        :return: str
        """
        return self.__mac

    # end mac getter

    @mac.setter
    def mac(self, mac):
        """
        Set method mac changes the Client object's mac attribute.
        :param mac: The new MAC address.
            type: str
            default: none
            required yes
        :return:
        """
        self.__mac = mac

    # end mac setter

    @property
    def client_detail(self):
        """
        Get method client_detail return's the Client's state information
        :return: dict
        """
        return self.__client_detail

    # end client_detail getter

    def get_client_detail(self):
        """
        Get method get_client_detail makes a call to Cisco DNAC, retrieves the Client's state information, stores it in
        the client_detail attribute, and also returns the results for further processing.
        :return: dict
        """
        if self.__mac in ILLEGAL_MAC_ADDRS:
            raise DnacApiError(
                MODULE, 'get_client_detail', ILLEGAL_MAC, '',
                '', self.__mac, '', ''
            )
        time = TimeStamp()
        query = '?timestamp=%s&macAddress=%s' % (time, self.__mac)
        url = self.dnac.url + self.resource + query
        detail, status = self.crud.get(url,
                                       headers=self.dnac.hdrs,
                                       verify=self.verify,
                                       timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_client_detail', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(detail)
            )
        self.__client_detail = detail
        return self.__client_detail

    # end get_client_detail()

# end class Client()

