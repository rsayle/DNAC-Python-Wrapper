#!/usr/bin/env python

from base64 import b64encode

class BasicAuth(object):
    '''
    Class BasicAuth stores the username and password for basic authorization
    of an HTTP request and then encodes it as "username:password" in
    Base64 format.  The encoded string is sent to the HTTP server.  Any
    time either values of username and password change, the object
    automatically updates the encoded string.

    Attributes:
        user: The username for logging into the server.
            type: str
            scope: public
            default: None
        passwd: The user's password for logging into the server.
            type: str
            scope: public
            default: None
        creds: The Base64 encoded string "username:password" that is
               transmitted to the server for logging into it.
            type: base64 encoded string
            scope: public
            default: base64 encoded string "user:passwd"
        hdr: a string for constructing CRUD request headers.
            type: str
            scope: public
            default: "'Authorization': 'Basic <base64 encoded string>'"
        hdrs: a dict for constructing CRUD request headers.
            type: dict
            scope: public
            default: {'Authorization' : 'Basic <base64 encoded string>'}
    '''

    def __init__(self, user="", passwd=""):
        '''
        The __init__ method initializes a BasicAuth object.  It takes in
        a username and password, sets the __user and __passwd, respectively,
        and then uses those values to create a base64 encoded string for
        the __creds attribute, a header string for __hdr, and a header
        dictionary for __hdrs.
 
        Parameters:
            user: The username for logging into an HTTP server.
                type: str
                default: None
                required: Yes
            passwd: The password for logging into an HTTP server.
                type: str
                default: None
                required: Yes

        Return Values:
            BasicAuth object: The newly constructed basic authntication
                              instance.

        Usage: b = BasicAuth(user="<username>", passwd="<password>")
        '''
        self.__user = user
        self.__passwd = passwd
        self.__creds = b64encode(user + ":" + passwd)
        self.__hdr = "\'Authorization\': \'Basic " + \
                      self.__creds + \
                      "\'"
        self.__hdrs = {'Authorization' : ("Basic " + self.__creds)}

    def __str__(self):
        '''
        String handler for a BasicAuth object.  Returns the base64
        encoded string "<username>:<password>".
        '''
        return self.creds

    @property
    def user(self):
        '''
        Get method user returns the value of attribute __user.

        Parameters:
            None

        Return Values:
            str: The user's login name.

        Usage:
            b = BasicAuth(user="<username>", passwd="<password>")
            b.user
        '''
        return self.__user

    @user.setter
    def user(self, user):
        '''
        Set method user changes the value of __user to the username
        provided as its parameter.  In addition, it automatically
        updates the values of __creds, __hdr and __hdrs to account for
        the change.

        Parameters:
            user: The new username for logging into an HTTP server.
                type: str
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            b = BasicAuth(user="<username>", passwd="<password>")
            b.user = "<username>"
        '''
        self.__user = user
        self.__creds = b64encode(user + ":" + self.__passwd)
        self.__hdr = "\'Authorization\': \'Basic " + self.__creds + "\'"
        self.__hdrs = {'Authorization' : ("Basic " + self.__creds)}

    @property
    def passwd(self):
        '''
        Get method user returns the value of attribute __passwd.

        Parameters:
            None

        Return Values:
            str: The user's password.

        Usage:
            b = BasicAuth(user="<username>", passwd="<password>")
            b.passwd
        '''
        return self.__passwd

    @passwd.setter
    def passwd(self, passwd):
        '''
        Set method passwd changes the value of __passwd to the password
        provided as its parameter.  In addition, it automatically
        updates the values of __creds, __hdr and __hdrs to account for
        the change.

        Parameters:
            passwd: The new password for logging into an HTTP server.
                type: str
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            b = BasicAuth(user="<username>", passwd="<password>")
            b.passwd = "<password>"
        '''
        self.__passwd = passwd
        self.__creds = b64encode(self.__user + ":" + passwd)
        self.__hdr = "\'Authorization\': \'Basic " + self.__creds + "\'"
        self.__hdrs = {'Authorization' : ("Basic " + self.__creds)}

    @property
    def creds(self):
        '''
        Get method creds returns the value of attribute __creds.

        Parameters:
            None

        Return Values:
            str: The base64 encoded string "<username>:<password>"

        Usage:
            b = BasicAuth(user="<username>", passwd="<password>")
            b.creds
        '''
        return self.__creds

    @creds.setter
    def creds(self, creds):
        '''
        Set method creds changes the value of __creds to the string
        provided as its parameter.  Use a Base64 encoded string whose
        format is "username:password".  In addition, creds automatically
        updates the values of __hdr and __hdrs to account for
        the change.

        Parameters:
            passwd: The new password for logging into an HTTP server.
                type: str
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            b = BasicAuth(user="<username>", passwd="<password>")
            b.passwd = "<password>"
        '''
        self.__creds = creds
        self.__hdr = "\'Authorization\': \'Basic " + self.__creds + "\'"
        self.__hdrs = {'Authorization' : ("Basic " + self.__creds)}

    @property
    def hdr(self):
        '''
        Get method hdr returns the value of attribute __hdr.

        Parameters:
            None

        Return Values:
            str: A string containing the base64 formatted credentials
                  that can be used to make CRUD requests.  The format looks
                  like "'Authorization': 'Basic <base64 encoded string>'"

        Usage:
            b = BasicAuth(user="<username>", passwd="<password>")
            b.hdr
        '''
        return self.__hdr

    @hdr.setter
    def hdr(self, hdr):
        '''
        Set method hdr changes the value of __hdr to the string
        provided as its parameter.  Use a string whose format is
        "'Authorization': 'Basic <base64 encoded username:password>'"

        Parameters:
            hdr: The new hdr for logging into an HTTP server.
                type: str
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            b = BasicAuth(user="<username>", passwd="<password>")
            b.hdr = "'Authorization': 'Basic <base64 encoded username:password>'"
        '''
        self.__hdr = hdr

    @property
    def hdrs(self):
        '''
        Get method hdrs returns the value of attribute __hdrs.

        Parameters:
            None

        Return Values:
            dict: A dictionary containing the base64 formatted credentials
                  that can be used to make CRUD requests.  The format looks
                  like {'Authorization': 'Basic <base64 encoded string>'}

        Usage:
            b = BasicAuth(user="<username>", passwd="<password>")
            b.hdrs
        '''
        return self.__hdrs

    @hdrs.setter
    def hdrs(self, hdrs):
        '''
        Set method hdrs changes the value of __hdrs to the dictionary
        provided as its parameter.  Use a dictionary whose format is
        {'Authorization': 'Basic <base64 encoded username:password>'}

        Parameters:
            hdrs: The new hdrs for logging into an HTTP server.
                type: dict
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            b = BasicAuth(user="<username>", passwd="<password>")
            b.hdrs = {'Authorization': 'Basic <base64 encoded username:password>'}
        '''
        self.__hdrs = hdrs

## end class BasicAuth()

## begin unit test

if __name__ == '__main__':

    b = BasicAuth()
    
    print "  user      = " + b.user
    print "  passwd      = " + b.passwd
    print "  creds      = " + b.creds
    print "  str(basicauth) = " + str(b)
    print "  basicauth.hdr  = " + b.hdr
    print "  basicauth.hdrs = " + str(b.hdrs)
    print
    print "Changing user..."
    b.user = "admin"
    print
    print "  user      = " + b.user
    print "  passwd      = " + b.passwd
    print "  creds      = " + b.creds
    print "  str(basicauth) = " + str(b)
    print "  basicauth.hdr  = " + b.hdr
    print "  basicauth.hdrs = " + str(b.hdrs)
    print
    print "Changing passwd..."
    b.passwd = "C!sco123"
    print
    print "  user      = " + b.user
    print "  passwd      = " + b.passwd
    print "  creds      = " + b.creds
    print "  str(basicauth) = " + str(b)
    print "  basicauth.hdr  = " + b.hdr
    print "  basicauth.hdrs = " + str(b.hdrs)
    print


