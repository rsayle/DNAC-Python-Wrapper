
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

__version__ = '1.2.10.2'
__author__ = 'Robert Sayle <rsayle@cisco.com>'
__all__ = [
    'basicauth',
    'client',
    'commandrunner',
    'crud',
    'ctype',
    'deployment',
    'dnac_config',
    'dnacapi',
    'file',
    'networkdevice',
    'site',
    'task',
    'template',
    'timestamp',
    'xauthtoken'
]

# globals
MODULE = 'dnac'
SUPPORTED_DNAC_VERSIONS = ['1.2.8', '1.2.10']

# Dnac errors
UNKNOWN_ERROR = 'Unknown error'
UNSUPPORTED_DNAC_VERSION = 'Unsupported Cisco DNA Center version'
NO_DNAC_PATH = 'No path to the Cisco DNA Center cluster'
DNAC_PATH = 'Set an FQDN or IP address for Cisco DNA Center in dnac_config.py'

# Dnac exception class - all others inherit from this one


class DnacError(Exception):
    """
    DnacError is an exception class for any errors specific to setting
    up and maintaining a connection with a Cisco DNA Center cluster.

    Attributes:
        None
    """

    def __init__(self, msg):
        """
        DnacError's __init__ method passes a message to its parent class.

        Parameters:
            msg: An error message indicating the problem.  Current values
                 include:
                    UNKNOWN_ERROR="Unknown error"
                    UNSUPPORTED_DNAC_VERSION="Unsupported Cisco DNA
                                              Center version"

        Return Values:
            DnacError object: the new exception.

        Usage:
            if version in SUPPORTED_DNAC_VERSIONS:
                self.__version = version
            else:
                raise DnacError(
                    UNSUPPORTED_DNAC_VERSION + ": %s" % version
                               )
        """
        super(DnacError, self).__init__(msg)

# end class DnacError()


class Dnac(object):
    """
    The Dnac class simplifies making API calls to a Cisco DNA Center
    cluster.  It maintains the base URL of an API call as well as its
    headers that specify authentication for initial login, authorization
    for subsequent API calls, and the content type format each API response
    should return.

    All Dnac objects use the data in dnac_config.py to set its attributes.
    See the comments in dnac_config.py for an explanation of each setting.

    Upon instantiation, a Dnac object uses the values in the config file
    to perform the initial login, retrieve an XAuth token from Cisco DNAC,
    sets the content type for responses, and creates a base URL for
    issuing API calls.

    Dnac objects store DnacApi objects in its api dictionary.  Do not
    create a DnacApi object.  Instead, instantiate the API objects that
    inherit from the DnacApi class.  When creating a DnacApi child object,
    give it a friendly name that can be used to access it later in a script.
    When created, these objects automatically add themselves to Dnac's api.
    In addition, they keep a reference to the Dnac container and use it
    for constructing API calls to the cluster.

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
        Dnac's __init__ method creates a new Dnac object based upon the
        values of the constants in dnac_config.py.  This is the preferred
        way to control Dnac's configuration, but if desired, each one
        can be overridden using key word arguments.

        __init__ also performs the initial login to the Cisco DNA Center
        cluster and gets an authorization token for subsequent API calls.

        Parameters:
            version:
                str: The version Cisco DNAC software running on the cluster.
                default: DNAC_VERSION
                required: no
            name:
                str: The FQDN used to reach the Cisco DNAC cluster.
                default: DNAC_NAME
                required: no
            ip:
                str: An IPv4 address used to reach the Cisco DNAC cluster
                     when an FQDN is not available.
                default: DNAC_IP
                required: no
            port:
                int: The TCP port for communicating with Cisco DNAC.
                default: DNAC_PORT
                required: no
            user:
                string: The administrator's name for logging into Cisco
                        DNAC.
                default: DNAC_USER
                required: no
            passwd:
                str: The administrator's password for logging into Cisco
                     DNAC.
                default: DNAC_PASSWD
                required: no
            content_type:
                str: The content type for API responses.
                default: DNAC_CONTENT_TYPE
                required: no

        Return Values:
            Dnac object: A new Dnac instance.

        Usage:
            d = Dnac()
            newD = Dnac(user='operator', passwd='l3tm3in!')
        """
        if version in SUPPORTED_DNAC_VERSIONS:
            self.__version = version
        else:
            raise DnacError(
                UNSUPPORTED_DNAC_VERSION + ": %s" % version
                           )
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

# end __init__()

    @property
    def version(self):
        """
        Get method version returns the value of __version, the version of
        Cisco DNA Center software running on the cluster.

        Parameters:
            none

        Return Values:
            str: The Cisco DNAC cluster software version.

        Usage:
            d = Dnac()
            ver = d.version
        """
        return self.__version

# end version getter

    @property
    def name(self):
        """
        Get method name returns the value of __version, Cisco DNAC's FQDN.

        Parameters:
            none

        Return Values:
            str: Cisco DNA Center's fully qualified domain name.

        Usage:
            d = Dnac()
            fqdn = d.name
        """
        return self.__name

# end name getter

    @property
    def ip(self):
        """
        Get method name returns the value of __ip, Cisco DNAC's IP address.

        Parameters:
            none

        Return Values:
            str: Cisco DNA Center's IPv4 address.

        Usage:
            d = Dnac()
            ip = d.ip
        """
        return self.__ip

# end ip getter

    @property
    def port(self):
        """
        Get method port returns the value of __ip, the TCP port Cisco
        DNAC uses.

        Parameters:
            none

        Return Values:
            int: Cisco DNA Center's TCP port for communication.

        Usage:
            d = Dnac()
            port = d.port
        """
        return self.__port

# end port getter

    @property
    def ctype(self):
        """
        Get method ctype returns the value of __ctype, a CType object that
        sets the content type for all DnacApi responses.

        Parameters:
            none

        Return Values:
            Ctype object: The content type Cisco DNA Center returns in
                          responses.

        Usage:
            d = Dnac()
            print str(d.ctype)
        """
        return self.__ctype

# end ctype getter

    @property
    def bauth(self):
        """
        Get method bauth returns the value of __bauth, a BasicAuth object
        for logging into Cisco DNA Center.

        Parameters:
            none

        Return Values:
            BasicAuth object: An object containing the base64 encoded
                              crednetials for logging into Cisco DNA Center.

        Usage:
            d = Dnac()
            print str(d.bauth)
        """
        return self.__bauth

# end bauth getter

    @property
    def xauth(self):
        """
        Get method xauth returns the value of __xauth, an XAuthToken
        for authorizing API calls to Cisco DNA Center.

        Parameters:
            none

        Return Values:
            BasicAuth object: An object containing the base64 encoded
                              credentials for logging into Cisco DNA Center.

        Usage:
            d = Dnac()
            print str(d.bauth)
        """
        return self.__xauth

# end xauth getter

    @property
    def api(self):
        """
        Get method api returns the value of __api, the dict holding all
        of the instantiated APIs.

        Parameters:
            none

        Return Values:
            dict: The dictionary of all of Dnac's APIs.

        Usage:
            d = Dnac()
            api = d.api
        """
        return self.__api

# end api getter

    @property
    def url(self):
        """
        The url method formats a base URL for reaching a Cisco DNA Center
        cluster.  It combines either Dnac's name (preferred) or its ip with
        its port.  If neither values are set, then it returns and empty
        string.

        url is decorated as a property so that it can be used like an
        attribute's get method.

        DnacApi objects use this method to build their API calls.

        Parameters:
            none

        Return Values:
            str: A URL for constructing an API call.

        Usage:
            d = Dnac()
            url = d.url
        """
        # prefer FQDN over IP address
        if bool(self.name):  # FQDN is set
            return 'https://%s:%s' % (self.name, self.port)
        elif bool(self.ip):  # IP address is set
            return 'https://%s:%s' % (self.ip, self.port)
        else:  # no way to reach DNA Center
            raise DnacError(
                '%s: %s: %s: %s' % (MODULE, 'url', NO_DNAC_PATH, DNAC_PATH)
                           )

# end url()

    def get_new_token(self):
        """
        Class method getNewToken instructs Dnac to get a new x-auth-token
        value using its __xauth instance.

        Parameters:
            none

        Return Values:
            none

        Usage:
            d = Dnac()
            d.getNewToken()
        """
        self.__xauth.get_token()

# end getNewToken()

    @property
    def hdrs(self):
        """
        The hdrs method returns a dictionary containing the hdrs values
        of __ctype and __xauth.  In other words, it provides the headers
        structure for making CRUD calls to a Cisco DNA Center cluster.

        The children classes of DnacApi use this function to complete
        their API calls.

        The method is decorated as a property so that it can be used
        just like any attribute's get method.

        Parameters:
            none

        Return Values:
            dict: The object used as CRUD headers when communicating with
                  a Cisco DNAC cluster.

        Usage:
            d = Dnac()
            headers = d.headers
        """
        h = {}
        h.update(self.__ctype.hdrs)
        h.update(self.__xauth.hdrs)
        return h

# end hdrs()

# end class Dnac()

# begin unit test


if __name__ == '__main__':

    import pprint
    from dnac.networkdevice import NetworkDevice

    pp = pprint.PrettyPrinter(indent=4)

    d = Dnac()

    print('DNAC:')
    print('  name        = ' + d.name)
    print('  version     = ' + d.version)
    print('  ip          = ' + d.ip)
    print('  port        = ' + d.port)
    print('  ctype       = ' + str(type(d.ctype)))
    print('  str(ctype)  = ' + str(d.ctype))
    print('  ctype.ctype = ' + d.ctype.ctype)
    print('  ctype.hdrs  = ' + str(d.ctype.hdrs))
    print('  bauth       = ' + str(type(d.bauth)))
    print('  str(bauth)  = ' + str(d.bauth))
    print('  bauth.creds = ' + d.bauth.creds)
    print('  bauth.hdrs  = ' + str(d.bauth.hdrs))
    print('  xauth       = ' + str(type(d.xauth)))
    print('  str(xauth)  = ' + str(d.xauth))
    print('  xauth.token = ' + d.xauth.token)
    print('  xauth.hdrs  = ' + str(d.xauth.hdrs))
    print('  api         = ' + str(d.api))
    print('  url         = ' + d.url)
    print('  hdrs        = ' + str(type(d.hdrs)))
    print('  hdrs        = ' + str(d.hdrs))
    print()

    print('Adding network-device API...')

    nd = NetworkDevice(d, 'network-device')
    d.api[nd.name] = nd

    print('  is in api             = ' + str(nd.name in d.api))
    print('  api["network-device"] = ' + str(d.api[nd.name]))
    print()

    print('Using network-device API...')
    print()

    resp = d.api[nd.name].get_device_by_name('DC1-A3850.cisco.com')

    print('  response = ')
    pp.pprint(resp)
    print()

    print('Clearing all APIs...')
    
    d.api.clear()

    print()
    print('  api = ' + str(d.api))
    print()

    print('Testing exceptions...')
    
    def raise_dnac_error(msg):
        raise DnacError(msg)

    eMsgs = [UNKNOWN_ERROR,
             NO_DNAC_PATH,
             DNAC_PATH] 
    
    for msg in eMsgs:
        try:
            raise_dnac_error(msg)
        except DnacError as e:
            print(str(type(e)) + " = " + str(e))

    print()
    print('Dnac unit test complete.')
