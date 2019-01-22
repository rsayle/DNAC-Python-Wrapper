#!/usr/bin/env python

class CType(object):
    '''
    Class CType stores the content type a user wants a CRUD API to return.

    Attributes:
        ctype: The content type to return.  Valid types include:
                "applicaion/json"
                "application/xml"
            type: str
            scope: public
            default: "application/json"
        hdr: a string for constructing CRUD request headers
            type: str
            scope: public
            default: "'Content-Type': application/json"
        hdrs: a dict for constructing CRUD request headers
            type: dict
            scope: public
            default: {'Content-Type': application/json}
    '''

    def __init__(self, contentType="application/json"):
        '''
        Method __init__ initializes a CType object.
 
        Parameters:
            contentType: content type to return.  Valid types include:
                         "applicaion/json"
                         "application/xml"
               type: str
               default: "application/json"
               required: No
 
        Return Values:
            CType object: The newly constructed content type object.

        Usage: c = CType()
               c = CType(contentType="<content type>")
        '''
        self.__ctype = contentType
        self.__hdr = "\'Content-Type\': " + contentType
        self.__hdrs = {'Content-Type': contentType}

    def __str__(self):
        '''
        String handler for a CType object.

        Usage: c = CType()
               str(c)
        '''
        return self.ctype

    @property
    def ctype(self):
        '''
        Get method ctype returns the string value of __ctype.

        Parameters:
            None

        Return Values:
            str: The content type selected.

        Usage: c = CType()
               c.ctype
        '''
        return self.__ctype

    @ctype.setter
    def ctype(self, ctype):
        '''
        Set method ctype assigns a new content type string to __ctype
        and then resets the values of __hdr and __hdrs accordingly.

        Parameters:
            ctype: The new content type for an HTTP server to return.
                type: str
                default: None
                required: Yes

        Return Values:
            None

        Usage: c = CType()
               c.ctype = "<content Type>"
        '''
        self.__ctype = ctype
        self.hdr = "\'Content-Type\': " + ctype
        self.hdrs = {'Content-Type': ctype}

    @property
    def hdr(self):
        '''
        Get method hdr returns the string value of __hdr.

        Parameters:
            None

        Return Values:
            str: A string formatted as "'Content-Type': '<ctype>'"
                 which can be used to construct headers for CRUD
                 requests.

        Usage: c = CType()
               c.hdr
        '''
        return self.__hdr

    @hdr.setter
    def hdr(self, hdr):
        '''
        Set method hdr assigns a new content type string to __hdr that
        instructs the HTTP server how to format the data it returns.
        Use a string whose format is "'Content-Type': '<content type>'".

        Parameters:
            hdr: The new header string for indicating the desired
                 content type the HTTP server should return.  
                 type: str
                 default: None
                 required: Yes

        Return Values:
            None

        Usage: c = CType()
               c.hdr = "'Content-Type': '<content type>'"
        '''
        self.__hdr = hdr

    @property
    def hdrs(self):
        '''
        Get method hdrs returns the string value of __hdrs.

        Parameters:
            None

        Return Values:
            dict: The dictionary {'Content-Type': '<ctype>'}, which
                  can be used to build headers for CRUD requests

        Usage: c = CType()
               c.hdrs
        '''
        return self.__hdrs

    @hdrs.setter
    def hdrs(self, hdrs):
        '''
        Set method hdrs assigns a new content type dictionary to __hdrs.

        Parameters:
            hdrs: The new headers dictionary for building CRUD requests.
                  Use the format {'Content-Type': '<ctype>'}.
                 type: dict
                 default: None
                 required: Yes

        Return Values:
            None

        Usage: c = CType()
               c.hdrs = {'Content-Type': '<content type>'}
        '''
        self.__hdrs = hdrs

## end class CType()

# begin unit test

if  __name__ == '__main__':

    c = CType()
    
    print "  ctype      = " + c.ctype
    print "  str(ctype) = " + str(c)
    print "  ctype.hdr  = " + c.hdr
    print "  ctype.hdrs = " + str(c.hdrs)
    print
    print "Changing ctype..."
    c.ctype = "application/xml"
    print
    print "  ctype      = " + c.ctype
    print "  str(ctype) = " + str(c)
    print "  ctype.hdr  = " + c.hdr
    print "  ctype.hdrs = " + str(c.hdrs)
    print


