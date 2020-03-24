
# globals

JSON = 'application/json'
XML = 'application/xml'


class CType(object):
    """
    Class CType stores the content type a user wants a CRUD API to return.

    Attributes:
        ctype: The content type to return.  Valid types include:
                application/json
                application/xml
            type: str
            scope: protected
            default: application/json
        hdrs: a dict for constructing CRUD request headers
            type: dict
            scope: public
            default: {'Content-Type': 'application/json'}
    """

    def __init__(self, content_type=JSON):
        """
        Method __init__ initializes a CType object.
        :param content_type: content type to return.  Valid types include:
                         application/json
                         application/xml
             type: str
             default: application/json
             required: no
        """
        self.__ctype = content_type
        self.__hdrs = {'Content-Type': self.__ctype}

    def __str__(self):
        """
        String handler for a CType object.
        :return: str
        """
        return self.__ctype

    @property
    def ctype(self):
        """
        Get method ctype returns the string value of __ctype.
        :return: str
        """
        return self.__ctype

    @property
    def hdrs(self):
        """
        Get method hdrs returns the string value of __hdrs.
        :return: dict
        """
        return self.__hdrs

# end class CType()

