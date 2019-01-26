#!/usr/bin/env python

from dnac import DnacError, SUPPORTED_DNAC_VERSIONS
from crud import Crud

## exceptions

## DNAC API errors
UNKNOWN_REQUEST_ERROR="Unexpected API request error"
REQUEST_NOT_OK="API response from DNAC is not OK"
REQUEST_NOT_ACCEPTED="DNAC did not accept the request"

class DnacApiError(Exception):

    def _init__(self, msg):
        super(DnacApiError, self).__init__(msg)

## end class DnacApiError

## end exceptions

class DnacApi(object):
    '''
    DnacApi is a virtual class for other classes that will implement
    API calls to Cisco DNA Center.  Inherit from this class when creating
    other classes to perform API requests.  This class is not intended
    to be directly instantiated and provides no logic for making API
    calls nor handling the data returned.  Child instances perform
    these tasks.

    Attributes:
        dnac: A reference to the Dnac object that houses all the DnacApis.
            type: Dnac object
            default: None
        name: A user friendly name for accessing the DnacAapi object
              in Cisco DNAC's API, i.e. Dnac.api{}
            type: str
            default: None
        respath: The resource path to the API call.  Each child class
                 derives its resource path based upon the version of Cisco
                 DNA Center being used.  Programmers should not change
                 this value.
            type: str
            default: None
        filter: A request filter for the Cisco DNAC API response.
            type: str
            default: None
        verify: A flag indicating whether or not to authenticate Cisco
                DNAC's certificate when making the API call.
            type: boolean
            default: False
        timeout: The time in seconds to wait for Cisco DNAC's response
                 before declaring the cluster unavailable.
            type: int
            default: 5
    '''
    
    def __init__(self, \
                 dnac, \
                 name, \
                 resourcePath, \
                 requestFilter="", \
                 verify=False, \
                 timeout=5):
        '''
        Class method __init__ creates a new DnacApi objects and sets its
        attribute values.  When instantiating a new DnacApi object provide
        a reference to the Dnac object that holds the APIs, a name used
        to access this object from Dnac.api{}, and the resource path for
        the API call itself.  In addition, the object adds itself into
        Dnac.api{} for reference when making API calls.

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: None
                required: Yes
            name: A user friendly name for find this API in the Dnac object.
                type: str
                default: None
                required: Yes
            resourcePath: The API call to Cisco DNAC.
                type: str
                default: None
                required: Yes
            requestFilter: An expression of filtering Cisco DNAC's response.
                type: str
                default: None
                required: No
            verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: No
            timeout: The number of seconds to wait for Cisco DNAC's response.
                type: int
                default: 5
                required: No

        Return Values:
            DnacApi object: a new DnacApi object.

        Usage:
            None.  This is a virtual class.
        '''
        self.__dnac = dnac
        self.__name = name
        self.__respath = resourcePath
        self.__filter = requestFilter
        self.__verify = verify
        self.__timeout = timeout
        self.__crud = Crud()

        # place the new API in Dnac's api dictionary
        self.__dnac.addApi(self.__name, self)

## end __init__()

    @property
    def result(self):
        return self.__crud.result

## end result getter

    @property
    def dnac(self):
        '''
        Get method dnac returns the reference to the Dnac instance that
        stores this object.

        Parameters:
            None

        Return Values:
            Dnac object: The Dnac object container.

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(dnac, name, respath)
            dnac = dapi.dnac
        '''
        return self.__dnac

    @dnac.setter
    def dnac(self, dnac):
        '''
        Set method dnac updates the __dnac attribute to point to a new
        Dnac object.

        Parameters:
            dnac: Dnac object
            default: none
            Required: Yes

        Return Values:
            None

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(dnac, name, respath)
            newDnac = Dnac()
            dapi.dnac = newDnac
        '''
        self.__dnac = dnac

    @property
    def name(self):
        '''
        Get method name returns __name, a user friendly name for accessing
        this object in Dnac's API store, namely Dnac.api{}

        Parameters:
            None

        Return Values:
            str: The DnacApi object's name

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(dnac, name, respath)
            dapi.name
        '''
        return self.__name

    @name.setter
    def name(self, name):
        '''
        Set method name updates the __name attribute thus renaming a
        DnacApi instance.

        Parameters:
            name: str
            default: none
            Required: Yes

        Return Values:
            None

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(dnac, name, respath)
            dapi.name = "aNewName"
        '''
        self.__name = name

    @property
    def respath(self):
        '''
        Get method respath returns __respath, which is the API call to
        Cisco DNAC.  In child classes, use this method to form request by
        appending it to Cisco DNAC's base url, i.e. Dnac.url.

        Parameters:
            None

        Return Values:
            str: The API call.

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            d = Dnac()
            dapi = DnacApi(d, name, respath)
            apicall = d.url + dapi.respath
        '''
        return self.__respath

    @respath.setter
    def respath(self, resourcePath):
        '''
        Set method respath updates the __respath attribute to a new
        value for the API call.

        Parameters:
            respath: str
            default: none
            Required: Yes

        Return Values:
            None

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(dnac, name, respath)
            dapi.respath = "/a/new/resource/path"
        '''
        self.__respath = resourcePath

    @property
    def filter(self):
        '''
        Get method filter returns __filter, a string used to control
        Cisco DNAC's response to the API call.  Use the filter to create
        a URL for the API call.

        Parameters:
            None

        Return Values:
            str: A filter string.

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            d = Dnac()
            dapi = DnacApi(d, name, respath)
            url = d.url + dapi.respath + dapi.filter
        '''
        return self.__filter

    @filter.setter
    def filter(self, requestFilter):
        '''
        Set method filter updates the __respath attribute to a new
        value for the API call.

        Parameters:
            respath: str
            default: none
            Required: Yes

        Return Values:
            None

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(dnac, name, respath)
            dapi.respath = "/a/new/resource/path"
        '''
        self.__filter = requestFilter

    @property
    def verify(self):
        '''
        Get method verify returns value of __verify, which is used to 
        determine whether or not to check Cisco DNAC's certificate upon
        making an API call.

        Parameters:
            None

        Return Values:
            boolean: True to check the cert; otherwise, False

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(d, name, respath)
            dapi.verify
        '''
        return self.__verify

    @verify.setter
    def verify(self, verify):
        '''
        Set method verify updates the __verify attribute to a new
        value for the API call.

        Parameters:
            verify: boolean
            default: none
            Required: Yes

        Return Values:
            None

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(dnac, name, respath)
            dapi.verify = True
        '''
        self.__verify = verify

    @property
    def timeout(self):
        '''
        Get method timeout returns the value of attribute __timeout.  The
        value returned represents the number of seconds to wait for the
        HTTP server to respond to an API request

        Parameters:
            None

        Return Values:
            int: time to wait in seconds for a response

        Usage:
            dapi = DnacApi(dnac, name, respath)
            dapi.timeout
        '''
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout):
        '''
        Set method timeout changes the attribute __timeout to the value
        of timeout, which is the number of seconds to wait for the server
        to respond before declaring Cisco DNAC unavailable.

        Parameters:
            timeout: int
            default: None
            required: Yes

        Return Values:
            None

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(dnac, name, respath)
            dapi.timeout = 10
        '''
        self.__timeout = timeout

## end class DnacApi()

## begin unit test

if  __name__ == '__main__':

    from dnac import Dnac

    d = Dnac()
    dapi = DnacApi(d, "aName", "/a/resource/path")

    print "DnacApi:"
    print
    print "  dnac           = " + str(type(dapi.dnac))
    print "  name           = " + dapi.name
    print "  respath        = " + dapi.respath
    print "  filter         = " + dapi.filter
    print "  verify         = " + str(dapi.verify)
    print "  timeout        = " + str(dapi.timeout)
    print "  isInApi        = " + str(d.isInApi(dapi.name))
    api = d.api
    print "  compare apis   = " + str(api == dapi)
    print
    print "Changing the attributes and assigning to a new Dnac()..."
    print

    newD = Dnac()
    dapi.name = "aNewName"
    dapi.respath = "/a/new/resource/path"
    dapi.filter = "a=newFilter"
    dapi.verify = True
    dapi.timeout = 10
    newD.addApi(dapi.name, dapi)

    print "  dnac           = " + str(type(dapi.dnac))
    print "  name           = " + dapi.name
    print "  respath        = " + dapi.respath
    print "  filter         = " + dapi.filter
    print "  verify         = " + str(dapi.verify)
    print "  timeout        = " + str(dapi.timeout)
    print "  isInApi        = " + str(newD.isInApi(dapi.name))
    api = newD.api[dapi.name]
    print "  compare apis   = " + str(api == dapi)
    print "  d.isInApi      = " + str(d.isInApi(dapi.name))
    print
    print "Testing exceptions..."
    print

    def raiseDnacApiError(msg):
        raise DnacApiError(msg)

    errors = (UNKNOWN_REQUEST_ERROR,
              REQUEST_NOT_OK,
              REQUEST_NOT_ACCEPTED)

    for error in errors:
        try:
            raiseDnacApiError(error)
        except DnacApiError, e:
            print str(type(e)) + " = " + str(e)

    print
    print "DnacApi: unit test complete."


