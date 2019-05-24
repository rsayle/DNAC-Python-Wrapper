
import json
import requests

# error messages
INVALID_RESPONSE = "Invalid response to API call"


class XAuthTokenError(Exception):
    """
    The XAuthTokenError exception class, derived from Exception, indicates
    any problems specific to requesting a token from Cisco DNA Center.

    Attributes:
        none
    """

    def __init__(self, msg):
        """
        XAuthTokenErrors's __init__ method passes a message to its
        parent class.

        Parameters:
            msg: An error message indicating the problem.  Current values
                 include:
                    INVALID_RESPONSE="Invalid response to API call"

        Return Values:
            XAuthTokenError object: the new exception.

        Usage:
            raise XAuthTokenError(INVALID_RESPONSE)
        """
        super(XAuthTokenError, self).__init__(msg)

# end class XAuthTokenError

# end exceptions


class XAuthToken(object):
    """
    Class XAuthToken stores a token used to authorize Cisco DNAC API
    calls.

    Dnac objects contain one XAuthToken for all of its DnacApi instances
    to reference when making a request to Cisco DNAC.  Use the
    Dnac.token class method to access the current token value instead
    of referencing the Dnac.xauth attribute, which is an instantiation
    of this class.  As necessary, use Dnac.get_new_token to refresh the
    x-auth-token value.

    Attributes:
        url: The base URL for contacting Cisco DNAC.
            type: str
            default: none
            scope: protected
        bauth: A basic authentication object for requesting a token
               from Cisco DNAC.
            type: BasicAuth object
            default: none
            scope: protected
        ctype: A content type object for requesting a token from Cisco DNAC.
            type: CType object
            default: CType('application/json')
            scope: Ppotected
        resource: The resource path used to request a token from Cisco DNAC.
            type: str
            default: '/api/system/v1/auth/token'
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
        token: The x-auth-token used to authorize API calls.
            type: str
            default: None
            scope: protected
        hdrs: The headers for requesting an x-auth-token from Cisco DNAC.
            type: dict
            default: none
            scope: protected
    """

    def __init__(self,
                 url,
                 basic_auth,
                 content_type,
                 resource='/api/system/v1/auth/token',
                 verify=False,
                 timeout=5):
        """
        The __init__ method initializes an XAuthToken object.  It takes
        a URL pointing to the Cisco DNAC cluster as well as both a BasicAuth
        and CType objects for constructing the token request.  When creating
        a Dnac object, the object's __init__ method passes its base URL
        (Dnac.url), its BasicAuth object (Dnac.bauth) and its chosen
        content type (Dnac.ctype).  This ensures that the XAuthToken
        instance (Dnac.xauth) remains consistent with all of the DnacApi
        objects in use, i.e. any changes to the basic authentication or to
        the content type used remain the same when calling on the XAuthToken.

        Parameters:
             url: The URL for reaching Cisco DNAC.
                 type: str
                 default: none
                 required: yes
             basic_auth: A BasicAuth object for logging into Cisco DNAC.
                 type: BasicAuth object
                 default: none
                 required: yes
             content_type: A CType object indicating the token's format
                         requested from Cisco DNAC
                 type: CType object
                 default: none
                 required: yes
             resource: The resource path used to request a token.
                 type: str
                 default: '/api/system/v1/auth/token'
                 required: no
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
             XAuthToken object: the newly constructed XAuthToken.

        Usage:
             x = XAuthToken(url, bauth, ctype)
        """
        self.__url = url
        self.__bauth = basic_auth
        self.__ctype = content_type
        self.__resource = resource
        self.__token = ''
        self.__verify = verify
        self.__timeout = timeout
        self.__hdrs = {}

    def __str__(self):
        """
        String handler for an XAuthToken object.  Returns the current
        value of __token.

        Parameters:
            none

        Return Values:
            str: The token's value.

        Usage:
            x = XAuthToken(url, bauth, ctype)
            str(x)
        """
        return self.__token

    @property
    def url(self):
        """
        Get method url returns the value of attribute __url.  URL is the
        base path to an HTTP server.

        Parameters:
            none

        Return Values:
            str: The base URL used to reach the HTTP server.

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.url
        """
        return self.__url

    @property
    def bauth(self):
        """
        Get method bauth returns the value of attribute __bauth, a
        BasicAuth object for logging into an HTTP server.

        Parameters:
            none

        Return Values:
            BasicAuth object: The HTTP basic authentication used to
                              request an x-auth-token from the server.

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.bauth
        """
        return self.__bauth

    @property
    def ctype(self):
        """
        Get method ctype returns the value of attribute __ctype, a
        CType object indicating the content type a user wants the
        HTTP server to return.

        Parameters:
            none

        Return Values:
            CType object: An object with the content type that the
                          server should provide in its response

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.ctype
        """
        return self.__ctype

    @property
    def resource(self):
        """
        Get method resource returns the value of attribute __resource, the
        resource path used to request an x-auth-token.

        Parameters:
            none

        Return Values:
            str: A path to the server's token request API.

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.resource
        """
        return self.__resource

    @property
    def verify(self):
        """
        Get method verify returns the value of attribute __verify.  Verify
        determines whether the HTTP server's certificate should be
        validated or not.

        Parameters:
            none

        Return Values:
            boolean: True if the certificate should be verified, else False

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.verify
        """
        return self.__verify

    @property
    def timeout(self):
        """
        Get method timeout returns the value of attribute __timeout.  The
        value returned represents the number of seconds to wait for the
        HTTP server to return an x-auth-token.

        Parameters:
            none

        Return Values:
            int: time to wait in seconds for a response

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.timeout
        """
        return self.__timeout

    @property
    def token(self):
        """
        Get method token returns the value of attribute __token, which is
        the x-auth-token value used by other API calls to authenticate
        with the HTTP server.

        Parameters:
            none

        Return Values:
            str: the token's value

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.token
        """
        return self.__token

    def get_token(self):
        """
        Class method getToken causes the XAuthToken instance to send a
        request to the server for a new x-auth-token.  The returned
        result gets stored in __token and then the function updates the
        object's __hdrs dictionary with the new token's value before
        returning the token to the calling script.

        Parameters:
            none

        Return values:
            str : the token's value

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.getToken()      # token gets saved in x
            t = x.getToken()  # token gets saved in x and returned to t
        """
        url = self.__url + self.__resource
        hdrs = {}
        hdrs.update(self.bauth.hdrs)
        hdrs.update(self.ctype.hdrs)
        resp = requests.request('POST',
                                url,
                                headers=hdrs,
                                verify=self.__verify,
                                timeout=self.__timeout)
        if resp.status_code != requests.codes.ok:
            raise XAuthTokenError(
                'XAuthToken: getToken: %s: %s: %i: expected %i' %
                (INVALID_RESPONSE, url, resp.status_code, requests.codes.ok)
                                  )
        self.__token = str(json.loads(resp.text)['Token'])
        self.__hdrs['X-Auth-Token'] = self.__token
        return self.__token

    @property
    def hdrs(self):
        """
        Get method hdrs returns the value of attribute __hdrs, a dict
        whose value is {'X-Auth-Token': '<token>'] and can be used to
        construct CRUD headers for authenticating calls to a server.

        Usage:
            x = XAuthToken(url, bauth, ctype)
            x.hdrs
        """
        return self.__hdrs

# end class XAuthToken()

# begin unit test


if __name__ == '__main__':

    from dnac.dnac import BasicAuth
    from dnac.dnac import CType
    
    d = 'https://denlab-en-dnac.cisco.com'
    b = BasicAuth('admin', 'C!sco123')
    c = CType('application/json')
    x = XAuthToken(d, b, c)

    print('XAuthToken:')
    print()
    print('  url      = ' + x.url)
    print('  bauth    = ' + str(type(x.bauth)))
    print('  bauth    = ' + str(x.bauth))
    print('  ctype    = ' + str(type(x.ctype)))
    print('  ctype    = ' + str(x.ctype))
    print('  resource = ' + x.resource)
    print('  token    = ' + x.token)
    print('  verify   = ' + str(x.verify))
    print('  timeout  = ' + str(x.timeout))
    print('  hdrs     = ' + str(x.hdrs))
    print()
    print('Getting a token...')
    print()
    x.get_token()
    print()
    print('  url      = ' + x.url)
    print('  bauth    = ' + str(type(x.bauth)))
    print('  bauth    = ' + str(x.bauth))
    print('  ctype    = ' + str(type(x.ctype)))
    print('  ctype    = ' + str(x.ctype))
    print('  resource = ' + x.resource)
    print('  token    = ' + x.token)
    print('  verify   = ' + str(x.verify))
    print('  timeout  = ' + str(x.timeout))
    print('  hdrs     = ' + str(x.hdrs))
    print()
    print('Testing exceptions...')
    print()

    def raise_xauthtoken_error(msg):
        raise XAuthTokenError(msg)

    errors = [INVALID_RESPONSE]

    for e in errors:
        try:
            raise_xauthtoken_error(e)
        except XAuthTokenError as e:
            print(str(type(e)) + ' = ' + str(e))

    print()
    print('XAuthToken: unit test complete.')

