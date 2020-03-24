
from dnac.xauthtoken import XAuthToken
from dnac.basicauth import BasicAuth
from dnac.ctype import CType
from dnac.dnac_config import DNAC_NAME, \
                             DNAC_IP, \
                             DNAC_VERSION, \
                             DNAC_PORT, \
                             DNAC_USER, \
                             DNAC_PASSWD, \
                             DNAC_CONTENT_TYPE

__version__ = '1.3.1.4'
__author__ = 'Robert Sayle <rsayle@cisco.com>'
__all__ = [
    'basicauth',
    'client',
    'commandrunner',
    'commandrunner_task',
    'config_archive',
    'crud',
    'ctype',
    'deployment',
    'device_archive',
    'device_archive_task',
    'dnac_config',
    'dnacapi',
    'file',
    '__init__',
    'networkdevice',
    'project',
    'site',
    'site_hierarchy',
    'task',
    'template',
    'timestamp',
    'version',
    'xauthtoken'
]

# globals
MODULE = 'dnac'
SUPPORTED_DNAC_VERSIONS = ['1.2.8', '1.2.10', '1.3.0.2', '1.3.0.3', '1.3.1.3', '1.3.1.4']

# Dnac errors
UNKNOWN_ERROR = 'Unknown error'
UNSUPPORTED_DNAC_VERSION = 'Unsupported Cisco DNA Center version'
NO_DNAC_PATH = ''
NO_DNAC_PATH_ERROR = 'No path to the Cisco DNA Center cluster'
NO_DNAC_PATH_RESOLUTION = 'Set an FQDN or IP address for Cisco DNA Center in dnac_config.py'

# Dnac exception class - all others inherit from this one


class DnacError(Exception):
    """
    DnacError is an exception class for any errors specific to setting up and maintaining a connection with a Cisco DNA
    Center cluster.

    Attributes:
        None
    """

    def __init__(self, msg):
        """
        DnacError's __init__ method passes a message to its parent class.
        :param msg: An error message indicating the problem.  Current values
        """
        super(DnacError, self).__init__(msg)

    # end __init__()

# end class DnacError()


class Dnac(object):
    """
    The Dnac class simplifies making API calls to a Cisco DNA Center cluster.  It maintains the base URL of an API call
    as well as its headers that specify authentication for initial login, authorization for subsequent API calls, and
    the content type format each API response should return.

    All Dnac objects use the data in dnac_config.py to set its attributes. See the comments in dnac_config.py for an
    explanation of each setting.

    Upon instantiation, a Dnac object uses the values in the config file to perform the initial login, retrieve an
    XAuth token from Cisco DNAC, sets the content type for responses, and creates a base URL for issuing API calls.

    Dnac objects store DnacApi objects in its api dictionary.  Do not create a DnacApi object.  Instead, instantiate
    the API objects that inherit from the DnacApi class.  When creating a DnacApi child object, give it a friendly name
    that can be used to access it later in a script. When created, these objects automatically add themselves to Dnac's
    api. In addition, they keep a reference to the Dnac container and use it for constructing API calls to the cluster.

    Attributes:
        version:
            str: The version Cisco DNAC software running on the cluster.
            default: DNAC_VERSION
            scope: protected
        name:
            str: The FQDN used to reach the Cisco DNAC cluster.
            default: DNAC_NAME
            scope: protected
        ip:
            str: An IPv4 address used to reach the Cisco DNAC cluster when
                 an FQDN is not available.
            default: DNAC_IP
            scope: protected
        port:
            int: The TCP port for communicating with Cisco DNAC.
            default: DNAC_PORT
            scope: protected
        ctype:
            Ctype object: The content type for API responses.
            default: DNAC_CONTENT_TYPE
            scope: protected
        user:
            string: The administrator's name for logging into Cisco DNAC.
            default: DNAC_USER
            scope: private
        passwd:
            str: The administrator's password for logging into Cisco DNAC.
            default: DNAC_PASSWD
            scope: private
        bauth:
            BasicAuth object: The base64 encoded username and password for
                              basic HTTP authentication to Cisco DNAC.
            default: The base64 encoded string "<user>:<passwd>".
            scope: protected
        xauth:
            XAuthToken object: The x-auth-token for authorizing API calls
                               after performing a basic authentication.
            default: An x-auth-token retrieved from Cisco DNAC when logging
                     in with a basic authentication.
            scope: protected
        api:
            dict: The DnacApi store for referencing API calls.
            default: {}
            scope: protected

    Usage:
        # It's very simple to create a Dnac object:
        d = Dnac()

        # Now make an API object, for example, a NetworkDevice and pass
        # it the Dnac instance you just created:
        nd = NetworkDevice(d, 'aNetworkDevice')

        # The API object will already be in Dnac.api so just use it!
        pprint.PrettyPrint(d.api['aNetworkDevice'].getAllDevices())

        # That's it!  Now wasn't that easier than constructing the API
        # call yourself?
    """

    def __init__(self,
                 version=DNAC_VERSION,
                 name=DNAC_NAME,
                 ip=DNAC_IP,
                 port=DNAC_PORT,
                 user=DNAC_USER,
                 passwd=DNAC_PASSWD,
                 content_type=DNAC_CONTENT_TYPE):
        """
        Dnac's __init__ method creates a new Dnac object based upon the values of the constants in dnac_config.py.
        This is the preferred way to control Dnac's configuration, but if desired, each one can be overridden using
        key word arguments.

        __init__ also performs the initial login to the Cisco DNA Center cluster and gets an authorization token for
        subsequent API calls.

        :param version: The version Cisco DNAC software running on the cluster.
            type: str
            default: DNAC_VERSION
            required: no
        :param name: The FQDN used to reach the Cisco DNAC cluster.
            type: str
            default: DNAC_NAME
            required: no
        :param ip: An IPv4 address used to reach the Cisco DNAC cluster when an FQDN is not available.
            type: str
            default: DNAC_IP
            required: no
        :param port: The TCP port for communicating with Cisco DNAC.
            type: str
            default: DNAC_PORT
            required: no
        :param user: The administrator's name for logging into Cisco DNAC.
            type: str
            default: DNAC_USER
            required: no
        :param passwd: The administrator's password for logging into Cisco DNAC.
            type: str
            default: DNAC_PASSWD
            required: no
        :param content_type: The content type for API responses.
            type: str
            default: DNAC_CONTENT_TYPE
            required: no
        """
        if version in SUPPORTED_DNAC_VERSIONS:
            self.__version = version
        else:
            raise DnacError('%s: %s' % (UNSUPPORTED_DNAC_VERSION, version))
        if name == NO_DNAC_PATH and ip == NO_DNAC_PATH:
            raise DnacError('%s: %s' % (NO_DNAC_PATH_ERROR, NO_DNAC_PATH_RESOLUTION))
        self.__name = name
        self.__ip = ip
        self.__port = port
        self.__ctype = CType(content_type)
        self.__user = user
        self.__passwd = passwd
        self.__bauth = BasicAuth(self.__user, self.__passwd)
        self.__xauth = XAuthToken(self.url,
                                  self.__bauth,
                                  content_type=self.__ctype)
        # get an authorization token for all API calls
        self.__xauth.get_token()
        # create the store for all API instances
        self.__api = {}
        # add a placeholder for the site hierarchy
        self.__site_hierarchy = None

    # end __init__()

    @property
    def version(self):
        """
        Returns the version of Cisco DNA Center software running on the cluster.
        :return: str
        """
        return self.__version

    # end version getter

    @property
    def name(self):
        """
        Get method name returns the value of __version, Cisco DNAC's FQDN.
        :return: str
        """
        return self.__name

    # end name getter

    @property
    def ip(self):
        """
        Get method name returns the value of __ip, Cisco DNAC's IP address.
        :return: str
        """
        return self.__ip

# end ip getter

    @property
    def port(self):
        """
        Get method port returns the value of __ip, the TCP port Cisco DNAC uses.
        :return: str
        """
        return self.__port

    # end port getter

    @property
    def ctype(self):
        """
        Returns the value of __ctype, a CType object that sets the content type for all DnacApi responses.
        :return: Ctype object
        """
        return self.__ctype

    # end ctype getter

    @property
    def bauth(self):
        """
        Get method bauth returns the value of __bauth, a BasicAuth object for logging into Cisco DNA Center.
        :return: BasicAuth object
        """
        return self.__bauth

    # end bauth getter

    @property
    def xauth(self):
        """
        Get method xauth returns the value of __xauth, an XAuthToken for authorizing API calls to Cisco DNA Center.
        :return: XAuthToken object
        """
        return self.__xauth

    # end xauth getter

    @property
    def api(self):
        """
        Get method api returns the value of __api, the dict holding all of the instantiated APIs.
        :return: dict
        """
        return self.__api

    # end api getter

    @property
    def url(self):
        """
        The url method formats a base URL for reaching a Cisco DNA Center cluster.  It combines either Dnac's name
        (preferred) or its ip with its port.  If neither values are set, then it returns and empty string.

        url is decorated as a property so that it can be used like an attribute's get method.

        DnacApi objects use this method to build their API calls.

        :return: str
        """
        # prefer FQDN over IP address
        if bool(self.name):  # FQDN is set
            return 'https://%s:%s' % (self.name, self.port)
        elif bool(self.ip):  # IP address is set
            return 'https://%s:%s' % (self.ip, self.port)
        else:  # no way to reach DNA Center
            raise DnacError('%s: %s: %s: %s' % (MODULE, 'url', NO_DNAC_PATH, NO_DNAC_PATH_RESOLUTION))

    # end url getter

    def get_new_token(self):
        """
        Class method getNewToken instructs Dnac to get a new x-auth-token value using its __xauth instance.
        :return: XAuthToken object
        """
        return self.__xauth.get_token()

    # end getNewToken()

    @property
    def hdrs(self):
        """
        The hdrs method returns a dictionary containing the hdrs values of __ctype and __xauth.  In other words, it
        provides the headers structure for making CRUD calls to a Cisco DNA Center cluster.

        The children classes of DnacApi use this function to complete their API calls.

        The method is decorated as a property so that it can be used just like any attribute's get method.

        :return: dict
        """
        h = {}
        h.update(self.__ctype.hdrs)
        h.update(self.__xauth.hdrs)
        return h

    # end hdrs()

# end class Dnac()


