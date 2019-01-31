#!/usr/bin/env python

from dnac import DnacError, SUPPORTED_DNAC_VERSIONS
from crud import Crud

MODULE="dnacapi.py"

## exceptions

SAME_NAME="Attempted to reset an API name to the same value"
SAME_NAME_MSG="Changing an API's name to the same value will result in the object being deleted from the Dnac object's api store."
SAME_NAME_CAUSE="Check that other functions are not changing the name after you've already modified it."

class DnacApiError(Exception):
    '''
    DnacApiError is derived from Exception and used as the sole exception
    that all children classes of DnacApi.  In other words, object inherited
    from DnacApi, e.g. NetworkDevice and CommandRunner, all raise
    DnacApiError exceptions instead of defining their own classes.

    DnacApiError has no attributes itself, but its initialization method
    includes a rich parameter set to indicate the problem, where it
    happened and what its cause might be.  See the documentation for
    the __init__ method for an explanation of each parameter and an example
    of how to raise this exception.

    Attributes:
        None
    '''
    def __init__(self,
                 module,
                 function,
                 error,
                 url,
                 expectedValue,
                 receivedValue,
                 receivedMsg,
                 possibleCause):
        '''
        DnacApiError's __init__ method formats a message based on its
        parameters and then calls its parent class, Exception, to post it.

        Parameter:
            module: Name of the python module in which the error originated.
                type: str
                default: None
                required: Yes
            function: The function's name where the problem happened.
                type: str
                default: None
                required: Yes
            error: The error encountered.  Use one provided by the system
                   or create your own.
                type: str
                default: None
                required: Yes
            url: The full resource path used during an API call if
                 applicable.  If the exception is unrelated to an API call,
                 use an empty string.
                type: str
                default: None
                required: Yes
            expectedValue: The value(s) that should have been provided.  If
                           no value was expected, use an empty string.
                type: str
                default: None
                required: Yes
            receivedValue: The value that was handled and cause the program
                           to raise an exception.  Use an empty string if
                           no actual value caused the error.
                type: str
                default: None
                required: Yes
            receivedMsg: Any additional messaging received by the script
                         when the error occurred.  Use an empty string if
                         no additional message is available or create your
                         own message.
                type: str
                default: None
                required: Yes
            possibleCause: Developer's notes on why the exception was
                           thrown and any potential solutions.  Use hints
                           the system provides or create your own.  If
                           the cause or solution is unknown, use an empty
                           string for this parameter.
                type: str
                default: None
                require: Yes

        Return Values:
            DnacApiError object: the exception that gets thrown.

        Usage:
            if status != OK:
                raise DnacApiError(
                    MODULE, "getAllDevices", REQUEST_NOT_OK, url,
                    OK, status, ERROR_MSGS[status], str(results)
                                  )
        '''
        exceptionMsg = "%s: %s: %s: %s: expected = %s: received = %s: received message = %s: possible cause = %s" % \
            (module, function, error, url, expectedValue, 
             receivedValue, receivedMsg, possibleCause)
        super(DnacApiError, self).__init__(exceptionMsg)

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
        resource: The resource path to the API call.  Each child class
                  derives its resource path based upon the version of Cisco
                  DNA Center being used.  Programmers should not change
                  this value.
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
        crud: A Crud object used to making API calls.  This is a protected
              attribute that is wrapped by the get, put, post and update
              methods included in this class.
            type: Crud object
            default: Crud object
    '''
    
    def __init__(self, \
                 dnac, \
                 name, \
                 resource="", \
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
            resource: The API call to Cisco DNAC.
                type: str
                default: None
                required: Yes
            verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: No
            timeout: The number of seconds to wait for Cisco DNAC's
                     response before the cluster is declared unreachable
                     or unavailable.
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
        self.__resource = resource
        self.__verify = verify
        self.__timeout = timeout
        self.__crud = Crud()

        # place the new API in Dnac's api dictionary
        self.__dnac.api[self.__name] = self

## end __init__()

    @property
    def crud(self):
        '''
        Get method crud returns the reference to the Crud object this class
        uses to make RESTful API calls.  Use this function in order to
        access the Crud object's get, put, post and delete methods.

        Parameters:
            None

        Return Values:
            Crud object: The wrapped Crud object

        Usage:
            url = self.dnac.url + self.resource
            devices, status = self.crud.get(url,
                                            headers=self.dnac.hdrs,
                                            verify=self.verify,
                                            timeout=self.timeout)
        '''
        return self.__crud

## end crud getter

    @property
    def results(self):
        '''
        The results method is decorated as if it was an attribute of this
        class and can be used accordingly.  It returns the raw results
        stored in the class' Crud object obtained from an API call.

        Parameters:
            None

        Return Values:
            dict: The results of the API call.

        Usage:
            d = Dnac()
            # CommandRunner is a DnacApi
            cmd = CommandRunner('running-config')
            cmd.formatCmd('<uuid>', 'show run')
            cmd.runSync()
            print str(cmd.results)
        '''
        return self.__crud.results

## end results getter

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
            dapi = DnacApi(dnac, name, resource)
            dnac = dapi.dnac
        '''
        return self.__dnac

## end dnac getter

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
            dapi = DnacApi(dnac, name, resource)
            newDnac = Dnac()
            dapi.dnac = newDnac
        '''
        self.__dnac = dnac

## end dnac setter

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
            dapi = DnacApi(dnac, name, resource)
            dapi.name
        '''
        return self.__name

## end name getter

    @name.setter
    def name(self, name):
        '''
        Set method name updates the __name attribute thus renaming a
        DnacApi instance.  Since this attribute serves as the key into
        a Dnac object's api dictionary, this method also updates the
        api key.

        Parameters:
            name: str
            default: none
            Required: Yes

        Return Values:
            None

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(dnac, name, resource)
            dapi.name = "aNewName"
        '''
        if name == self.name:
            # could quietly return doing nothing but raising an error
            raise DnacApiError(
                MODULE, "name setter", SAME_NAME, "",
                "", name, SAME_NAME_MSG, SAME_NAME_CAUSE
                              )
        # save the original name
        oldname = self.__name
        # assign the new one
        self.__name = name
        # update the key in dnac.api{}
        self.dnac.api[self.__name] = self
        # remove the old key from Dnac's api{}
        if oldname in self.dnac.api:
            del self.dnac.api[oldname]

## end name setter

    @property
    def resource(self):
        '''
        Get method resource returns __resource, which is the API call to
        Cisco DNAC.  In child classes, use this method to form requests by
        appending it to Cisco DNAC's base url, i.e. Dnac.url.

        Parameters:
            None

        Return Values:
            str: The API call.

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            d = Dnac()
            dapi = DnacApi(d, name, resource)
            apicall = d.url + dapi.resource
        '''
        return self.__resource

## end resource getter

    @resource.setter
    def resource(self, resource):
        '''
        Set method resource updates the __resource attribute to a new
        value for the API call.

        Parameters:
            resource: str
            default: none
            Required: Yes

        Return Values:
            None

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(dnac, name, resource)
            dapi.resource = "/a/new/resource/path"
        '''
        self.__resource = resource

## end resource setter

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
            dapi = DnacApi(d, name, resource)
            dapi.verify
        '''
        return self.__verify

## end verify getter

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
            dapi = DnacApi(dnac, name, resource)
            dapi.verify = True
        '''
        self.__verify = verify

## end verify setter

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
            dapi = DnacApi(dnac, name, resource)
            dapi.timeout
        '''
        return self.__timeout

## end timeout getter

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
            dapi = DnacApi(dnac, name, resource)
            dapi.timeout = 10
        '''
        self.__timeout = timeout

## end timeout setter

## end class DnacApi()

## begin unit test

if  __name__ == '__main__':

    from dnac import Dnac

    d = Dnac()
    dapi = DnacApi(d, "aName", "/a/resource/path")

    print "DnacApi:"
    print
    print "  dnac            = " + str(type(dapi.dnac))
    print "  name            = " + dapi.name
    print "  crud            = " + str(type(dapi.crud))
    print "  results         = " + str(dapi.results)
    print "  resource        = " + dapi.resource
    print "  verify          = " + str(dapi.verify)
    print "  timeout         = " + str(dapi.timeout)
    print "  is in api       = " + str(dapi.name in dapi.dnac.api)
    print "  dapi            = " + str(dapi)
    print "  dapi in api     = " + str(d.api[dapi.name])
    print
    print "Changing the attributes..."
    print

    dapi.name = "aNewName"
    dapi.resource = "/a/new/resource/path"
    dapi.filter = "a=newFilter"
    dapi.verify = True
    dapi.timeout = 10

    print "  dnac            = " + str(type(dapi.dnac))
    print "  name            = " + dapi.name
    print "  crud            = " + str(type(dapi.crud))
    print "  results         = " + str(dapi.results)
    print "  resource        = " + dapi.resource
    print "  verify          = " + str(dapi.verify)
    print "  timeout         = " + str(dapi.timeout)
    print "  is in api (old) = " + str(dapi.name in "aName")
    print "  is in api (new) = " + str(dapi.name in dapi.dnac.api)
    print "  dapi            = " + str(dapi)
    print "  dapi in api     = " + str(d.api[dapi.name])
    print
    print "Making a get() call..."

    dapi.name = "network-device"
    dapi.resource = \
        "/api/v1/network-device/a0116157-3a02-4b8d-ad89-45f45ecad5da"
    dapi.verify = False
    url = d.url + dapi.resource
    results, status = dapi.crud.get(url,
                                    headers=dapi.dnac.hdrs,
                                    verify=dapi.verify,
                                    timeout=dapi.timeout)

    print "  status  = " + status
    print "  results = " + str(results)
    print
    print "Testing exception..."

    dapierror = DnacApiError(MODULE, "aFunc", "anError", "aUrl",
                             "this", "that", "aMsg", "aCause")

    print "  exception = " + str(dapierror)
    print 
    print "Raising exception..."
    print

    try:
        raise dapierror
    except DnacApiError, e:
            print e

    print
    print "DnacApi: unit test complete."

