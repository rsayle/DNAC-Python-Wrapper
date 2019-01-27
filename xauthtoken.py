#!/usr/bin/env python

from ctype import CType
from basicauth import BasicAuth
import requests
import json

## exceptions

## error messages

INVALID_RESPONSE="Invalid response to API call"

class XAuthTokenError(Exception):

    def __init__(self, msg):
        super(XAuthTokenError, self).__init__(msg)

## end class XAuthTokenError

## end exceptions

class XAuthToken(object):
    '''
    Class XAuthToken stores a token used to authenticate Cisco DNAC API
    calls.

    Dnac objects contain one XAuthToken instance for all of its DnacApi
    instances to reference when making a request to Cisco DNAC.  Use the
    Dnac.token class method to access the current token value instead
    of referencing the Dnac.xauth attribute, which is an instantiation
    of this class.

    Attributes:
        url: The base URL for contacting Cisco DNAC.
            type: str
            default: None
        bauth: A basic authentication object for requesting a token
               from Cisco DNAC.
            type: BasicAuth object
            default: None
        ctype: A content type object for requesting a token from Cisco DNAC.
            type: CType object
            default: CType("application/json")
        respath: The resource path used to request a token from Cisco DNAC.
            type: str
            default: "/api/system/v1/auth/token"
        verify: Flag indicating whether or not the request should verify
                Cisco DNAC's certificate.
            type: boolean
            default: False
        timeout: The number of seconds the request for a token should wait
                 before assuming Cisco DNAC is unavailable.
            type: int
            default: 5
    '''

    def __init__(self, \
                 url, \
                 basicAuth, \
                 contentType, \
                 resourcePath="/api/system/v1/auth/token", \
                 verify=False, \
                 timeout=5):
       '''
       The __init__ method initializes an XAuthToken object.  It takes
       a URL pointing to the Cisco DNAC cluster and a BasicAuth object for
       the token request.  When creating a Dnac object, the object's
       __init__ method passes its base URL (Dnac.url), its BasicAuth object
       (Dnac.__bauth) and its chosen content type (Dnac.__ctype).  This
       ensures that the XAuthToken instance (Dnac.__xauth) remains
       consistent with all of the DnacApi objects Dnac uses, i.e. any
       changes to the basic authentication or to the content type used
       remain the same when calling on the XAuthToken instance.

       Parameters:
            url: The URL for reaching Cisco DNAC.
                type: str
                default: None
                required: Yes
            basicAuth: A BasicAuth object for logging into Cisco DNAC.
                type: BasicAuth object
                default: None
                required: Yes
            conentType: A CType object indicating the token's format
                        requested from Cisco DNAC
                type: CType object
                default: CType("application/json")
                required: No
            resourcePath: The resource path used to request a token.
                type: str
                default: "/api/system/v1/auth/token"
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
            XAuthToken object: the newly constructed XAuthToken.

       Usage:
            x = XAuthToken(url, bauth, ctype)
       '''
       self.__url = url 
       self.__bauth = basicAuth 
       self.__ctype = contentType 
       self.__respath = resourcePath
       self.__token = ""
       self.__verify = verify
       self.__timeout = timeout
       self.__hdr = ""
       self.__hdrs = {}

    def __str__(self):
        '''
        String handler for an XAuthToken object.  Returns the current
        value of __token.

        Parameters:
            None

        Return Values:
            str: The token's value.

        Usage:
            x = XAuthToken(url, bauth, ctype)
            str(x)
        '''
        return self.__token

    @property
    def url(self):
        '''
        Get method url returns the value of attribute __url.  URL is the
        base path to an HTTP server.

        Parameters:
            None

        Return Values:
            str: The base URL used to reach the HTTP server.

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.url
        '''
        return self.__url

    @url.setter
    def url(self, url):
        '''
        Set method url changes the attribute __url to the value of url.
        Use a URL to an HTTP server.

        Parameters:
            url: str
            default: None
            required: Yes

        Return Values:
            None

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.url = "https://dnac.localdomain"
        '''
        self.__url = url

    @property
    def bauth(self):
        '''
        Get method bauth returns the value of attribute __bauth, a
        BasicAuth object for logging into an HTTP server.

        Parameters:
            None

        Return Values:
            BasicAuth object: The HTTP basic authentication used to
                              request an x-auth-token from the server.

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.url
        '''
        return self.__bauth

    @bauth.setter
    def bauth(self, bauth):
        '''
        Set method bauth changes the attribute __bauth to the value 
        of bauth.  Use a BasicAuth object set with the username and
        password for logging into an HTTP server.

        Parameters:
            bauth: BasicAuth object
            default: None
            required: Yes

        Return Values:
            None

        Usage:
            x = XAuthToken(url, bauth, ctype)
            newBasicAuth = BasicAuth(user="username", passwd="password")
            x.bauth = newBasicAuth
        '''
        self.__bauth = bauth

    @property
    def ctype(self):
        '''
        Get method ctype returns the value of attribute __ctype, a
        CType object indicating the content type a user wants the
        HTTP server to return.

        Parameters:
            None

        Return Values:
            CType object: An object with the content type that the 
                          server should provide in its response

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.ctype
        '''
        return self.__ctype

    @ctype.setter
    def ctype(self, ctype):
        '''
        Set method ctype changes the attribute __ctype to the value 
        of ctype.  Use a CType object with the desired content type
        the HTTP server should return.

        Parameters:
            ctype: Ctype object
            default: None
            required: Yes

        Return Values:
            None

        Usage:
            x = XAuthToken(url, bauth, ctype)
            newContentType = CType("application/xml")
            x.ctype = newContentType
        '''
        self.__ctype = ctype

    @property
    def respath(self):
        '''
        Get method respath returns the value of attribute __respath, the
        resource path used to request an x-auth-token.

        Parameters:
            None

        Return Values:
            str: A path to the server's token request API.

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.respath
        '''
        return self.__respath

    @respath.setter
    def respath(self, respath):
        '''
        Set method respath changes the attribute __respath to the value 
        of respath.  The resource path used should be an API call requesting
        an x-auth-token from an HTTP server

        Parameters:
            respath: string
            default: None
            required: Yes

        Return Values:
            None

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.respath = "/api/system/v1/auth/token"
        '''
        self.__respath = respath

    @property
    def verify(self):
        '''
        Get method verify returns the value of attribute __verify.  Verify
        determines whether the HTTP server's certificate should be 
        validated or not.

        Parameters:
            None

        Return Values:
            boolean: True if the certificate should be verified, else False

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.verify
        '''
        return self.__verify

    @verify.setter
    def verify(self, verify):
        '''
        Set method verify changes the attribute __verify to the value 
        of verify.  True validates a server's certificate; False does not.

        Parameters:
            verify: boolean
            default: None
            required: Yes

        Return Values:
            None

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.verify = True
        '''
        self.__verify = verify

    @property
    def timeout(self):
        '''
        Get method timeout returns the value of attribute __timeout.  The
        value returned represents the number of seconds to wait for the
        HTTP server to return an x-auth-token.

        Parameters:
            None

        Return Values:
            int: time to wait in seconds for a response

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.timeout
        '''
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout):
        '''
        Set method timeout changes the attribute __timeout to the value 
        of timeout, which is the number of seconds to wait for the server
        to return an x-auth-token before assuming it's unavailable.

        Parameters:
            timeout: int
            default: None
            required: Yes

        Return Values:
            int: The timeout in seconds.

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.timeout = 10
        '''
        self.__timeout = timeout

    @property
    def token(self):
        '''
        Get method token returns the value of attribute __token, which is
        the x-auth-token value used by other API calls to authenticate
        with the HTTP server.

        Parameters:
            None

        Return Values:
            str: the token's value

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.token
        '''
        return self.__token

    @token.setter
    def token(self, token):
        '''
        Set method token changes the attribute __token to the value 
        of token, an x-auth-token used by other API calls to authenticate
        with the server.

        Parameters:
            token: str
            default: None
            required: Yes

        Return Values:
            None

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.timeout = "<token>"
        '''
        self.__token = token

    def getToken(self):
        '''
        Class method getToken causes the XAuthToken instance to send a
        request to the server for a new x-auth-token.  The returned
        result gets stored in __token and then the function updates the
        object's _hdr and __hdrs with the new token's value before 
        returning the token to the script

        Parameters:
            None

        Return values:
            str : the token's value

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.getToken()     # token gets saved in x
            t = x.getToken() # token gets saved in x and returned to t
        '''
        url = self.url + self.respath
        hdrs = {}
        hdrs.update(self.bauth.hdrs)
        hdrs.update(self.ctype.hdrs)
        resp = requests.request("POST", \
                                url, \
                                headers=hdrs, \
                                verify=self.verify, \
                                timeout=self.timeout)
        if resp.status_code != requests.codes.ok:
            raise XAuthTokenError(
                "XAuthToken: getToken: %s: %s: %s: expected %s" % \
                (INVALID_RESPONSE, url, str(resp.status_code),
                str(requests.codes.ok))
                                  )
        self.__token = str(json.loads(resp.text)['Token'])
        self.hdr = "\'X-Auth-Token\': \'%s\'" % self.__token
        self.hdrs['X-Auth-Token'] = self.__token
        return self.__token

    @property
    def hdr(self):
        '''
        Get method hdr returns the value of attribute __hdr, a string
        whose value is "'X-Auth-Token': '<token>'" and can be used to
        construct CRUD headers for authenticating calls to the server.

        Parameters:
            None

        Return Values:
            str: An x-auth-token header string for CRUD calls.

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.hdr
        '''
        return self.__hdr

    @hdr.setter
    def hdr(self, hdr):
        '''
        Set method hdr changes the XAuthToken's __hdr to the string
        it is given.  Users are expected to format the string correctly
        for an x-auth-token.

        Parameters:
            hdr:
                str: An x-auth-token header string.
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            x = XAuthToken(url, bauth, ctype)
            header = "x-auth-token: <token>"
            x.hdr = header
        '''
        self.__hdr = hdr

    @property
    def hdrs(self):
        '''
        Get method hdrs returns the value of attribute __hdrs, a dict
        whose value is {'X-Auth-Token': '<token>'] and can be used to
        construct CRUD headers for authenticating calls to the server.

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.hdrs
        '''
        return self.__hdrs

    @hdrs.setter
    def hdrs(self, hdrs):
        '''
        Set method hdrs changes the XAuthToken's __hdrs to the dict
        it is given.  Users are expected to format the dict correctly
        for an x-auth-token.

        Parameters:
            hdr:
                dict: An x-auth-token header dictionary.
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            x = XAuthToken(url, bauth, ctype)
            headers = {'x-auth-token': '<token>'}
            x.hdrs = headers
        '''
        self.__hdrs = hdrs

## end class XAuthToken()

## begin unit test

if  __name__ == '__main__':

    from basicauth import BasicAuth
    from ctype import CType
    
    d = "https://denlab-en-dnac.cisco.com"
    b = BasicAuth(user="admin", passwd="C!sco123")
    c = CType("application/json")
    x = XAuthToken(d, b, c)
    
    print "  url    = " + x.url
    print "  bauth      = " + str(type(x.bauth))
    print "  bauth      = " + str(x.bauth)
    print "  ctype      = " + str(type(x.ctype))
    print "  ctype      = " + str(x.ctype)
    print "  respath    = " + x.respath
    print "  token      = " + x.token
    print "  verify     = " + str(x.verify)
    print "  timeout    = " + str(x.timeout)
    print "  hdr        = " + x.hdr
    print "  hdrs       = " + str(x.hdrs)
    print
    print "Getting a token..."
    print
    x.token = x.getToken()
    print
    print "  url        = " + x.url
    print "  bauth      = " + str(type(x.bauth))
    print "  bauth      = " + str(x.bauth)
    print "  ctype      = " + str(type(x.ctype))
    print "  ctype      = " + str(x.ctype)
    print "  respath    = " + x.respath
    print "  token      = " + x.token
    print "  verify     = " + str(x.verify)
    print "  timeout    = " + str(x.timeout)
    print "  hdr        = " + x.hdr
    print "  hdrs       = " + str(x.hdrs)
    print
    print "Testing exceptions..."
    print

    def raiseXAuthTokenError(msg):
        raise XAuthTokenError(msg)

    errors = [INVALID_RESPONSE]

    for e in errors:
        try:
            raiseXAuthTokenError(e)
        except XAuthTokenError, e:
            print str(type(e)) + " = " + str(e)

    print
    print "XAuthToken: unit test complete."

