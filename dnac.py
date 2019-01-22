#!/usr/bin/env python

from xauthtoken import XAuthToken
from basicauth import BasicAuth
from ctype import CType
from dnac_config import DNAC_NAME, \
                        DNAC_IP, \
                        DNAC_VERSION, \
                        DNAC_PORT, \
                        DNAC_USER, \
                        DNAC_PASSWD, \
                        DNAC_CONTENT_TYPE

class Dnac(object):
    '''
    The Dnac class simplifies making API calls to a Cisco DNA Center
    cluster.  It maintains the base URL of an API call as well as its
    headers that specify authentication for initial login, authorization
    for subsequent API calls, and the content type format each API response
    should return.

    All Dnac objects use the data in dnac_config.py to set its attributes.
    It is possible to override these settings when constructing a new
    Dnac object, but it is preferred that users defer to the config file
    instead.  See the comments in dnac_config.py for an explanation of
    each setting.

    Upon instantiation, a Dnac object uses the values in the config file
    to perform the initial login, retrieve an XAuth token from DNAC,
    sets the content type for responses, and creates a base URL for
    issuing API calls.

    Dnac objects store DnacApi objects in its api attribute, a dictionary
    whose keys are a user-friendly name for the DnacApi object and whose
    values are DnacApi instances.  Do not create a DnacApi object.  Instead,
    instantiate the API objects that inherit from the DnacApi class.  When
    created, these objects automatically add themselves to Dnac's api.
    In addition, they keep a reference to the Dnac container and use it
    for constructing API calls to the cluster.

    Attributes:
        version: 
            str: The version DNAC software running on the cluster.
            default: DNAC_VERSION
        name:
            str: The FQDN used to reach the DNAC cluster.
            default: DNAC_NAME
        ip:
            str: An IPv4 address used to reach the DNAC cluster when an
                 FQDN is not available.
            default: DNAC_IP
        port:
            int: The TCP port for communicating with DNAC.
            default: DNAC_PORT
        ctype:
            Ctype object: The content type for API responses.
            default: DNAC_CONTENT_TYPE
        user:
            string: The administrator's name for logging into DNAC.
            default: DNAC_USER
        passwd:
            str: The administrator's password for logging into DNAC.
            default: DNAC_PASSWD
        bauth:
            BasicAuth object: The base64 encoded username and password for
                              basic HTTP authentication to DNAC.
            default: The base64 encoded string "<user>:<passwd>".
        xauth:
            XAuthToken object: The x-auth-token for authorizing API calls
                               after performing a basic authenticaiton.
            default: An x-auth-token retrieved from DNAC when logging in
                     with a basic authentication.
        api:
            dict: The DnacApi store for referencing API calls.
            default: {}

    Usage:
        # It's very simple to create a Dnac object:
        d = Dnac()

        # Now make an API object, for example, a NetworkDevice and pass
        # it the Dnac instance you just created:
        nd = NetworkDevice(d, "aNetworkDevice")
    
        # The API object will already be in Dnac.api so just use it!
        devs = d.api['aNetworkDevice'].getAllDevices()

        # That's it!  Now wasn't that easier than constructing the API
        # call yourself?
    '''

    def __init__(self, \
                 version=DNAC_VERSION, \
                 name=DNAC_NAME, \
                 ip=DNAC_IP, \
                 port=DNAC_PORT, \
                 user=DNAC_USER, \
                 passwd=DNAC_PASSWD, \
                 contentType=DNAC_CONTENT_TYPE):
        '''
        Dnac's __init__ method creates a new Dnac object based upon the
        values of the constants in dnac_config.py.  This is the preferred
        way to control Dnac's configuration, but if desired, each one
        can be overridden using key word arguments.

        __init__ also peforms the initial login to the DNA Center cluster
        and gets an authorization token for subsequent API calls.

        Parameters:
            version: 
                str: The version DNAC software running on the cluster.
                default: DNAC_VERSION
            name:
                str: The FQDN used to reach the DNAC cluster.
                default: DNAC_NAME
            ip:
                str: An IPv4 address used to reach the DNAC cluster when an
                     FQDN is not available.
                default: DNAC_IP
            port:
                int: The TCP port for communicating with DNAC.
                default: DNAC_PORT
            user:
                string: The administrator's name for logging into DNAC.
                default: DNAC_USER
            passwd:
                str: The administrator's password for logging into DNAC.
                default: DNAC_PASSWD
            contentType:
                str: The content type for API responses.
                default: DNAC_CONTENT_TYPE

        Return Values:
            Dnac object: A new Dnac instance.

        Usage:
            d = Dnac()
            newD = Dnac(user="operator", passwd="l3tm3in!"
        '''
        self.__version = version
        self.__name = name
        self.__ip = ip
        self.__port = port
        self.__ctype = CType(contentType)
        self.__user = user
        self.__passwd = passwd
        self.__bauth = BasicAuth(self.__user, self.__passwd)
        self.__xauth = XAuthToken(self.url, \
                                  self.__bauth, \
                                  contentType=self.__ctype)
        self.__xauth.getToken()
        self.__api = {}

## end __init__()

    @property
    def version(self):
        '''
        Get method version returns the value of __version, the version of
        DNA Center software running on the cluster.
    
        Parameters:
            None
    
        Return Values:
            str: The DNAC cluster software version.
    
        Usage:
            d = Dnac()
            ver = d.version
        '''
        return self.__version

## end version getter

    @version.setter
    def version(self, version):
        '''
        Set method version changes __version's value to the given string.
    
        Parameters:
            str: The new DNAC software version.
            default: None
    
        Return Values:
            None
    
        Usage:
            d = Dnac()
            d.version = "1.2.6"
        '''
        self.__version = version

## end version setter

    @property
    def name(self):
        '''
        Get method name returns the value of __version, DNAC's FQDN.
    
        Parameters:
            None
    
        Return Values:
            str: DNA Center's fully qualified domain name.
    
        Usage:
            d = Dnac()
            fqdn = d.name
        '''
        return self.__name

## end name getter

    @name.setter
    def name(self, name):
        '''
        Set method name changes __name's value to the given FQDN.
    
        Parameters:
            str: The new DNAC fully qualified domain name.
            default: None
    
        Return Values:
            None
    
        Usage:
            d = Dnac()
            d.version = "1.2.6"
        '''
        self.__name = name

## end name setter

    @property
    def ip(self):
        '''
        Get method name returns the value of __ip, DNAC's IP address.
    
        Parameters:
            None
    
        Return Values:
            str: DNA Center's IPv4 address.
    
        Usage:
            d = Dnac()
            ip = d.ip
        '''
        return self.__ip

## ip getter

    @ip.setter
    def ip(self, ip):
        '''
        Set method ip changes __ip's value to the given IPv4 address.
    
        Parameters:
            str: The new DNAC IP address.
            default: None
    
        Return Values:
            None
    
        Usage:
            d = Dnac()
            d.version = "10.1.1.1"
        '''
        self.__ip = ip

## end ip setter

    @property
    def port(self):
        '''
        Get method port returns the value of __ip, the TCP port DNAC uses.
    
        Parameters:
            None
    
        Return Values:
            int: DNA Center's TCP port for communication.
    
        Usage:
            d = Dnac()
            port = d.port
        '''
        return self.__port

## end port getter

    @port.setter
    def port(self, port):
        '''
        Set method port changes __port's value to the given TCP port.
    
        Parameters:
            int: The new DNAC TCP port.
            default: None
    
        Return Values:
            None
    
        Usage:
            d = Dnac()
            d.port = 8088
        '''
        self.__port = port

## end port setter

    @property
    def user(self):
        '''
        Get method user returns the value of __user, an account name for
        logging into the DNAC cluster.
    
        Parameters:
            None
    
        Return Values:
            str: DNA Center's administrative user name.
    
        Usage:
            d = Dnac()
            username = d.name
        '''
        return self.__user

## end user getter

    @user.setter
    def user(self, user):
        '''
        Set method user changes __user's value to the username given.  When
        changing the username, a programmer should also change the password
        and then handle logging into DNAC with the new credentials and
        getting a new x-auth-token, i.e. recreating Dnac's BasicAuth and
        XAuthToken objects stored in __bauth and __xauth, respectively.
    
        Parameters:
            str: The new DNAC administator username.
            default: None
    
        Return Values:
            None
    
        Usage:
            d = Dnac()
            d.user = "operator"
        '''
        self.__user = user

## end user setter

    @property
    def passwd(self):
        '''
        Get method passwd returns the value of __passwd, the user's
        password for logging into the DNAC cluster.
    
        Parameters:
            None
    
        Return Values:
            str: DNA Center's administrative user's password.
    
        Usage:
            d = Dnac()
            password = d.passwd
        '''
        return self.__passwd

## end passwd getter

    @passwd.setter
    def passwd(self, passwd):
        '''
        Set method passwd changes __passwd's value to the password given.
        When changing the password, a programmer should also change the
        username and then handle logging into DNAC with the new credentials
        and getting a new x-auth-token, i.e. recreating Dnac's BasicAuth
        and XAuthToken objects stored in __bauth and __xauth, respectively.
    
        Parameters:
            str: The new DNAC administator username.
            default: None
    
        Return Values:
            None
    
        Usage:
            d = Dnac()
            d.user = "operator"
        '''
        self.passwd = passwd

## end passwd setter

    @property
    def ctype(self):
        '''
        Get method ctype returns the value of __ctype, a CType object that
        sets the content type for all DnacApi responses.
    
        Parameters:
            None
    
        Return Values:
            Ctype object: The content type DNA Center returns in responses.
    
        Usage:
            d = Dnac()
            print str(d.ctype)
        '''
        return self.__ctype

## end ctype getter

    @ctype.setter
    def ctype(self, ctype):
        '''
        Set method ctype changes the value of __ctype, a CType object that
        sets the content type for all DnacApi responses.
    
        Parameters:
            ctype: A CType object for directing DNAC what format to use when
                   responding to API calls.
    
        Return Values:
            None
    
        Usage:
            d = Dnac()
            d.ctype = CType(d, "application/xml")
        '''
        self.__ctype = ctype

## end ctype setter

    @property
    def bauth(self):
        '''
        Get method bauth returns the value of __bauth, a BasicAuth object
        for logging into DNA Center.
    
        Parameters:
            None
    
        Return Values:
            BasicAuth object: An object containing the base64 encoded
                              crednetials for logging into DNA Center.
    
        Usage:
            d = Dnac()
            print str(d.bauth)
        '''
        return self.__bauth

## end bauth getter

    @bauth.setter
    def bauth(self, bauth):
        '''
        Set method bauth changes the value of __bauth, a BasicAuth object
        used for logging into DNA Center.  If you change Dnac's bauth, you
        are also responsible for resetting Dnac's user and passwd as well
        as generating a new XAuthToken object.
    
        Parameters:
            bauth: A BasicAuth object for logging into DNA Center.
    
        Return Values:
            None
    
        Usage:
            d = Dnac()
            d.bauth = CType(d, "operator", "l3tm3in!")
        '''
        self.__bauth = bauth
        # get a new token
        self.xauth.token = self.xauth.getToken(self.__bauth.creds)

## end bauth setter

    @property
    def xauth(self):
        '''
        Get method xauth returns the value of __xauth, an XAuthToken
        for authorizing API calls to DNA Center.
    
        Parameters:
            None
    
        Return Values:
            BasicAuth object: An object containing the base64 encoded
                              crednetials for logging into DNA Center.
    
        Usage:
            d = Dnac()
            print str(d.bauth)
        '''
        return self.__xauth

## end xauth getter

    @xauth.setter
    def xauth(self, xauth):
        '''
        Set method xauth changes the value of __xauth, an XAuthToken
        instance for authorizing API calls after basic login succeeds.

        Parameters:
            xauth: An XAuthToken object for authorizing DNAC API calls.

        Return Values:
            None

        Usage:
            d = Dnac()
            d.xauth = XAuthToken(d)
        '''
        self.__xauth = xauth

## end xauth setter

    @property
    def api(self):
        '''
        Get method api returns the value of __api, the dict holding all
        of the instantiated APIs.
    
        Parameters:
            None
    
        Return Values:
            dict: The dictionary of all of Dnac's APIs.
    
        Usage:
            d = Dnac()
            api = d.api
        '''
        return self.__api

## end api getter

    @api.setter
    def api(self, api):
        '''
        Set method api changes __api's value to a new dictionary.

        Parameters:
            api: A dictionary of DnacApi objects.

        Return Values:
            None

        Usage:
            d = Dnac()
            # Unrealistic to do this
            d.api = {}
        '''
        self.__api = api

## end api setter

    def addApi(self, name, api):
        '''
        Class method addApi places a DnacApi object into Dnac's api store.
        DnacApi uses this method to automatically add itself to Dnac.

        Parameters:
            name:
                type: str
                default: None
                required: Yes
            api:
                type: DnacApi object
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, "nd")
            newD = Dnac()
            new.addApi("nd", newD)
        '''
        self.__api[name] = api

## end addApi()

    def deleteApi(self, name):
        '''
        The deleteApi method removes and destroys the named DnacApi.

        Parameters:
            name:
                type: str
                default: None
                required: yes

        Return Values:
            None

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, "nd")
            d.deleteApi("nd")
        '''
        del self.__api[name]

## end deleteApi()

    def deleteAllApis(self):
        '''
        deleteAllApis clears Dnac's api dictionary and destroys all of
        its elements.

        Parameters:
            None

        Return Values:
            None

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, "nd")
            d.deleteAllApis()
        '''
        self.__api.clear()

## end deleteAllApis()

    def isInApi(self, name):
        '''
        Method isInApi checks so see if the named API is located in Dnac's
        api store.

        Parameters:
            name:
                type: str
                default: None
                required: Yes

        Return Values:
            bool: True if the name matches an API's name; otherwise, False.

        Usage:
            d = Dnac()
            nd = NetworkDevice(d, "nd")
            if isInApi("nd"):
                print "It's in there!"
        '''
        return name in self.__api

## end isInApi()

    @property
    def url(self):
        '''
        The url method formats a base URL for reaching a DNA Center cluster.
        It combines either Dnac's name (preferred) or its ip with its port.
        If neither values are set, then it returns and empty string.

        url is decorated as a property so that it can be used like an
        attribute's get method.

        DnacApi objects use this method to build their API calls.

        Parameters:
            None

        Return Values:
            str: A URL for constructing an API call.

        Usage:
            d = Dnac()
            url = d.url
        '''
        # prefer FQDN over IP address
        if self.name != "":
            u = "https://" + \
                self.name + \
                ":" + \
                str(self.port)
            return u
        elif self.ip != "":
            u = "https://" + \
                self.ip + \
                ":" + \
                str(self.port)
            return u
        else:
            # rewrite to throw an exception
            return ""

## end url()

    def getNewToken(self):
        '''
        Class method getNewToken instructs Dnac to get a new x-auth-token
        value using its __xauth instance.

        Parameters:
            None

        Return Values:
            None

        Usage:
            d = Dnac()
            d.getNewToken()
        '''
        self.__xauth.getToken()

## end getNewToken()

    @property
    def hdrs(self):
        '''
        The hdrs method returns a dictionary containing the hdrs values
        of __ctype and __xauth.  In other words, it provides the headers
        structure for making CRUD calls to a DNA Center cluster.

        The children classes of DnacApi use this function to complete
        their API calls.

        The method is decorated as a property so that it can be used
        just like any attribute's get method.

        Parameters:
            None

        Return Values:
            dict: The object used as CRUD headers when communicating with
                  a DNAC cluster.

        Usage:
            d = Dnac()
            headers = d.headers
        '''
        h={}
        h.update(self.__ctype.hdrs)
        h.update(self.__xauth.hdrs)
        return h

## end hdrs()

## end class Dnac()

## begin unit test

if  __name__ == '__main__':

    d = Dnac()

    print "DNAC:"
    print "  name        = " + d.name
    print "  version     = " + d.version
    print "  ip          = " + d.ip
    print "  port        = " + d.port
    print "  user        = " + d.user
    print "  passwd      = " + d.passwd
    print "  ctype       = " + str(type(d.ctype))
    print "  str(ctype)  = " + str(d.ctype)
    print "  ctype.ctype = " + d.ctype.ctype
    print "  ctype.hdr   = " + d.ctype.hdr
    print "  ctype.hdrs  = " + str(d.ctype.hdrs)
    print "  bauth       = " + str(type(d.bauth))
    print "  str(bauth)  = " + str(d.bauth)
    print "  bauth.creds = " + d.bauth.creds
    print "  bauth.hdr   = " + d.bauth.hdr
    print "  bauth.hdrs  = " + str(d.bauth.hdrs)
    print "  xauth       = " + str(type(d.xauth))
    print "  str(xauth)  = " + str(d.xauth)
    print "  xauth.token = " + d.xauth.token
    print "  xauth.hdr   = " + d.xauth.hdr
    print "  xauth.hdrs  = " + str(d.xauth.hdrs)
    print "  api         = " + str(d.api)
    print "  url         = " + d.url
    print "  hdrs        = " + str(type(d.hdrs))
    print "  hdrs        = " + str(d.hdrs)
    print

    print "Changing attributes..."
    print "  <future test case>"
    print

    print "Adding network-device API..."
    from networkdevice import NetworkDevice

    nd = NetworkDevice(d, "network-device")
    d.addApi(nd.name, nd)

    print "  isInApi['network-device'] = " + str(d.isInApi(nd.name))
    print "  api['network-device']     = " + str(d.api[nd.name])
    print

    print "Using network-device API..."
    print

    resp = d.api[nd.name].getDeviceByName('DC1-A3850.cisco.com')

    print "  response = " + str(resp)
    print

    print "Clearing all APIs..."
    
    d.deleteAllApis()

    print
    print "  api = " + str(d.api)
    print
