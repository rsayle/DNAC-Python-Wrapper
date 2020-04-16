
from base64 import b64encode


class BasicAuth(object):
    """
    Class BasicAuth stores the username and password for basic authorization of an HTTP request and then encodes it as
    "username:password" in base64 format.  The encoded string is used to authenticate connections to an API server.
    """

    def __init__(self, user, passwd):
        """
        The __init__ method initializes a BasicAuth object.  It takes in a username and password, sets the __user and
        __passwd, respectively, and then uses those values to create a base64 encoded string for the __creds attribute
        and a header dictionary for __hdrs.

        Usage: b = BasicAuth(user, passwd)

        :param user: The username for logging into an HTTP server
            type: str
            required: yes
            default: none
        :param passwd: The password for logging into an HTTP server
            type: str
            required: yes
            default: none
        """
        self.__user = user
        self.__passwd = passwd
        self.__creds = self.make_creds()
        self.__hdrs = {'Authorization': ('Basic %s' % self.__creds)}

    def __str__(self):
        """
        String handler for a BasicAuth object.
        :return: base64 encoded string "<username>:<password>"
        """
        return self.__creds

    def make_creds(self):
        """
        Builds the base64 encoded string <username>:<password> for basic authentication to an API server.
        :return: base64 encoded str
        """
        credstr = '%s:%s' % (self.__user, self.__passwd)
        cred64 = b64encode(credstr.encode())
        return cred64.decode()

    @property
    def creds(self):
        """
        Getter method to retrieve the credentials stored in the object instance.
        :return: base64 encoded string
        """
        return self.__creds

    @property
    def hdrs(self):
        """
        Getter method that returns the format of a basic auth request for an API request.
        :return: dict of the form {'Authorization': 'Basic <base64 encoded credentials>'
        """
        return self.__hdrs

# end class BasicAuth()

