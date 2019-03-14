
from base64 import b64encode


class BasicAuth(object):
    """
    Class BasicAuth stores the username and password for basic authorization
    of an HTTP request and then encodes it as "username:password" in
    base64 format.  The encoded string is used to authenticate connections to
    an API server.

    Attributes:
        user: The username for logging into the server.
            type: str
            default: none
            scope: private
        passwd: The user's password for logging into the server.
            type: str
            default: none
            scope: private
        creds: The Base64 encoded string "username:password" that is
               transmitted to the server for logging into it.
            type: base64 encoded string
            default: base64 encoded string "user:passwd"
            scope: protected
        hdrs: a dict for constructing CRUD request headers.
            type: dict
            default: {'Authorization' : 'Basic <base64 encoded string>'}
            scope: protected
    """

    def __init__(self, user, passwd):
        """
        The __init__ method initializes a BasicAuth object.  It takes in
        a username and password, sets the __user and __passwd, respectively,
        and then uses those values to create a base64 encoded string for
        the __creds attribute and a header dictionary for __hdrs.

        Parameters:
            user: The username for logging into an HTTP server.
                type: str
                default: none
                required: Yes
            passwd: The password for logging into an HTTP server.
                type: str
                default: none
                required: Yes

        Return Values:
            BasicAuth object: The newly constructed basic authentication instance.

        Usage: b = BasicAuth(user, passwd)
        """
        self.__user = user
        self.__passwd = passwd
        self.__creds = self.make_creds()
        self.__hdrs = {'Authorization': ('Basic %s' % self.__creds)}

    def __str__(self):
        """
        String handler for a BasicAuth object.  Returns the base64 encoded string "<username>:<password>".
        """
        return self.__creds

    def make_creds(self):
        """
        Method make_creds builds the base64 encoded string <user>:<passwd> for basic authentication to an API server.

        Parameters:
            none

        Return Values:
            str: The base64 encoded string "<username>:<passwd>"

        Usage:
            b = BasicAuth(user, passwd)
            b.make_creds()
        """
        credstr = '%s:%s' % (self.__user, self.__passwd)
        cred64 = b64encode(credstr.encode())
        return cred64.decode()

    @property
    def creds(self):
        """
        Get method creds returns the value of attribute __creds.

        Parameters:
            none

        Return Values:
            str: The base64 encoded string "<username>:<password>"

        Usage:
            b = BasicAuth(user, passwd)
            b.creds
        """
        return self.__creds

    @property
    def hdrs(self):
        """
        Get method hdrs returns the value of attribute __hdrs.

        Parameters:
            none

        Return Values:
            dict: A dictionary containing the base64 formatted credentials
                  that can be used to make CRUD requests.  The format looks
                  like {'Authorization': 'Basic <base64 encoded string>'}

        Usage:
            b = BasicAuth(user, passwd)
            b.hdrs
        """
        return self.__hdrs

# end class BasicAuth()

# begin unit test


if __name__ == '__main__':

    b = BasicAuth('admin', 'C!sco123')

    print('BasicAuth:')
    print()
    print('  creds          = ' + b.creds)
    print('  str(basicauth) = ' + str(b))
    print('  basicauth.hdrs = ' + str(b.hdrs))
    print()
    print('BasicAuth unit test complete.')

