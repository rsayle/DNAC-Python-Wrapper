
import json
import requests

# error messages
INVALID_RESPONSE = "Invalid response to API call"


class XAuthTokenError(Exception):
    """
    The XAuthTokenError exception class, derived from Exception, indicates any problems specific to requesting a token
    from Cisco DNA Center.

    Attributes:
        none
    """

    def __init__(self, msg):
        """
        XAuthTokenErrors's __init__ method passes a message to its parent class.
        :param msg: An error message indicating the problem.
            type: str
            required: yes
            default: non
        """
        super(XAuthTokenError, self).__init__(msg)

# end class XAuthTokenError

# end exceptions


class XAuthToken(object):
    """
    Class XAuthToken stores a token used to authorize Cisco DNAC API calls.

    Dnac objects contain one XAuthToken for all of its DnacApi instances to reference when making a request to Cisco
    DNAC.  Use the Dnac.token class method to access the current token value instead of referencing the Dnac.xauth
    attribute, which is an instantiation of this class.  As necessary, use Dnac.get_new_token to refresh the
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
        The __init__ method initializes an XAuthToken object.  It takes a URL pointing to the Cisco DNAC cluster as
        well as both a BasicAuth and CType objects for constructing the token request.  When creating a Dnac object,
        the object's __init__ method passes its base URL (Dnac.url), its BasicAuth object (Dnac.bauth) and its chosen
        content type (Dnac.ctype).  This ensures that the XAuthToken instance (Dnac.xauth) remains consistent with all
        of the DnacApi objects in use, i.e. any changes to the basic authentication or to the content type used remain
        the same when calling on the XAuthToken.
        :param url: The URL for reaching Cisco DNAC.
            type: str
            default: none
            required: yes
        :param basic_auth: A BasicAuth object for logging into Cisco DNAC.
            type: BasicAuth object
            default: none
            required: yes
        :param content_type: A CType object indicating the token's format requested from Cisco DNAC
            type: CType object
            default: none
            required: yes
        :param resource: The resource path used to request a token.
            type: str
            default: '/api/system/v1/auth/token'
            required: no
        :param verify: A flag used to check Cisco DNAC's certificate.
            type: boolean
            default: False
            required: no
        :param timeout: The number of seconds to wait for Cisco DNAC's response.
            type: int
            default: 5
            required: no
        """
        self.__url = url
        self.__bauth = basic_auth
        self.__ctype = content_type
        self.__resource = resource
        self.__token = ''
        self.__verify = verify
        self.__timeout = timeout
        self.__hdrs = {}

    # end __init__()

    def __str__(self):
        """
        String handler for an XAuthToken object.  Returns the current value of __token.
        :return: str
        """
        return self.__token

    # end __str__

    @property
    def url(self):
        """
        Get method url returns the value of attribute __url.  URL is the base path to an HTTP server.
        :return: str
        """
        return self.__url

    # end url getter

    @property
    def bauth(self):
        """
        Get method bauth returns the value of attribute __bauth, a BasicAuth object for logging into an HTTP server.
        :return: BasicAuth object
        """
        return self.__bauth

    # end bauth getter

    @property
    def ctype(self):
        """
        Get method ctype returns the value of attribute __ctype, a CType object indicating the content type a user
        wants the HTTP server to return.
        :return: Ctype object
        """
        return self.__ctype

    # end ctype getter

    @property
    def resource(self):
        """
        Returns the value of attribute __resource, the resource path used to request an x-auth-token.
        :return: str
        """
        return self.__resource

    # end resource getter

    @property
    def verify(self):
        """
        Get method verify returns the value of attribute __verify.  Verify determines whether the HTTP server's
        certificate should be validated or not.
        :return: bool
        """
        return self.__verify

    # end verify getter

    @property
    def timeout(self):
        """
        Get method timeout returns the value of attribute __timeout.  The value returned represents the number of
        seconds to wait for the HTTP server to return an x-auth-token.
        :return: int
        """
        return self.__timeout

    # end timeout getter

    @property
    def token(self):
        """
        Get method token returns the value of attribute __token, which is the x-auth-token value used by other API
        calls to authenticate with the HTTP server.
        :return: str
        """
        return self.__token

    # end token getter

    def get_token(self):
        """
        Class method getToken causes the XAuthToken instance to send a request to the server for a new x-auth-token.
        The returned result gets stored in __token and then the function updates the object's __hdrs dictionary with
        the new token's value before returning the token to the calling script.
        :return: str
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

    # end get_token()

    @property
    def hdrs(self):
        """
        Get method hdrs returns the value of attribute __hdrs, a dict whose value is {'X-Auth-Token': '<token>'} and
        can be used to construct CRUD headers for authenticating calls to a server.
        :return: dict
        """
        return self.__hdrs

    # end hdrs getter

# end class XAuthToken()

