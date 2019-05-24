
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

        Parameters:
            content_type: content type to return.  Valid types include:
                         application/json
                         application/xml
               type: str
               default: application/json
               required: no

        Return Values:
            CType object: The newly constructed content type object.

        Usage: c = CType()
               c = CType(content_type='<content type>')
        """

        self.__ctype = content_type
        self.__hdrs = {'Content-Type': self.__ctype}

    def __str__(self):
        """
        String handler for a CType object.

        Usage: c = CType()
               str(c)
        """
        return self.__ctype

    @property
    def ctype(self):
        """
        Get method ctype returns the string value of __ctype.

        Parameters:
            none

        Return Values:
            str: The content type selected.

        Usage: c = CType()
               c.ctype
        """
        return self.__ctype

    @property
    def hdrs(self):
        """
        Get method hdrs returns the string value of __hdrs.

        Parameters:
            none

        Return Values:
            dict: The dictionary {'Content-Type': '<ctype>'}, which
                  can be used to build headers for CRUD requests

        Usage: c = CType()
               c.hdrs
        """
        return self.__hdrs

# end class CType()

# begin unit test


if __name__ == '__main__':
    c = CType()

    print('CType:')
    print()
    print('  ctype      = ' + c.ctype)
    print('  str(ctype) = ' + str(c))
    print('  ctype.hdrs = ' + str(c.hdrs))
    print()

