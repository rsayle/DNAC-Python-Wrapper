
from dnac.crud import Crud

MODULE = 'dnacapi.py'


class DnacApiError(Exception):
    """
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
        none
    """
    def __init__(self,
                 module,
                 function,
                 error,
                 url,
                 expected_value,
                 received_value,
                 received_msg,
                 cause_or_resolution):
        """
        DnacApiError's __init__ method formats a message based on its
        parameters and then calls its parent class, Exception, to post it.

        Parameter:
            module: Name of the python module in which the error originated.
                type: str
                default: none
                required: yes
            function: The function's name where the problem happened.
                type: str
                default: none
                required: yes
            error: The error encountered.  Use one provided by the system
                   or create your own.
                type: str
                default: none
                required: yes
            url: The full resource path used during an API call if
                 applicable.  If the exception is unrelated to an API call,
                 use an empty string.
                type: str
                default: none
                required: yes
            expected_value: The value(s) that should have been provided.  If
                            no value was expected, use an empty string.
                type: str
                default: none
                required: yes
            received_value: The value that was handled and cause the program
                            to raise an exception.  Use an empty string if
                            no actual value caused the error.
                type: str
                default: none
                required: yes
            received_msg: Any additional messaging received by the script
                          when the error occurred.  Use an empty string if
                          no additional message is available or create your
                          own message.
                type: str
                default: none
                required: yes
            cause_or_resolution: Developer's notes on why the exception was
                                 thrown and any potential solutions.  Use
                                 hints the system provides or create your
                                 own.  If the cause or solution is unknown,
                                 use an empty string for this parameter.
                type: str
                default: none
                require: yes

        Return Values:
            DnacApiError object: the exception that gets thrown.

        Usage:
            if status != OK:
                raise DnacApiError(
                    MODULE, 'getAllDevices', REQUEST_NOT_OK, url,
                    OK, status, ERROR_MSGS[status], str(results)
                                  )
        """
        exception_msg = \
            '%s: %s: %s: %s: expected = %s: received = %s: received message = %s: possible cause or resolution = %s' % \
            (module, function, error, url, expected_value, received_value, received_msg, cause_or_resolution)
        super(DnacApiError, self).__init__(exception_msg)

# end class DnacApiError


class DnacApi(object):
    """
    DnacApi is a virtual class for other classes that will implement
    API calls to Cisco DNA Center.  Inherit from this class when creating
    other classes to perform API requests.  This class is not intended
    to be directly instantiated and provides no logic for making API
    calls nor handling the data returned.  Child instances perform
    these tasks.

    Attributes:
        dnac: A reference to the Dnac object that houses all the DnacApis.
            type: Dnac object
            default: none
            scope: protected
        name: A user friendly name for accessing the DnacAapi object
              in Cisco DNAC's API, i.e. Dnac.api{}
            type: str
            default: none
            scope: protected
        resource: The resource path to the API call.  Each child class
                  derives its resource path based upon the version of Cisco
                  DNA Center being used.  Programmers should not change
                  this value.
            type: str
            default: None
            scope: protected
        crud: A Crud object used to making API calls.  This is a protected
              attribute that is wrapped by the get, put, post and update
              methods included in this class.
            type: Crud object
            default: Crud object
            scope: protected
        verify: A flag indicating whether or not to authenticate Cisco
                DNAC's certificate when making the API call.
            type: boolean
            default: False
            scope: protected
        timeout: The time in seconds to wait for Cisco DNAC's response
                 before declaring the cluster unavailable.
            type: int
            default: 5
            scope: protected
    """
    
    def __init__(self,
                 dnac,
                 name,
                 resource='',
                 verify=False,
                 timeout=5):
        """
        Class method __init__ creates a new DnacApi objects and sets its
        attribute values.  When instantiating a new DnacApi object provide
        a reference to the Dnac object that holds the APIs, a name used
        to access this object from Dnac.api{}, and the resource path for
        the API call itself.  In addition, the object adds itself into
        Dnac.api{} for reference when making API calls.

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: none
                required: yes
            name: A user friendly name for find this API in the Dnac object.
                type: str
                default: none
                required: yes
            resource: The API call to Cisco DNAC.
                type: str
                default: none
                required: yes, as a keyword argument
            verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: no
            timeout: The number of seconds to wait for Cisco DNAC's
                     response before the cluster is declared unreachable
                     or unavailable.
                type: int
                default: 5
                required: no

        Return Values:
            DnacApi object: a new DnacApi object.

        Usage:
            None.  This is a virtual class.
        """
        self.__dnac = dnac
        self.__name = name
        self.__resource = resource
        self.__verify = verify
        self.__timeout = timeout
        self.__crud = Crud()
        # place the new API in Dnac's api dictionary
        self.__dnac.api[self.__name] = self

# end __init__()

    @property
    def crud(self):
        """
        Get method crud returns the reference to the Crud object this class
        uses to make RESTful API calls.  Use this function in order to
        access the Crud object's get, put, post and delete methods.

        Parameters:
            none

        Return Values:
            Crud object: The wrapped Crud object

        Usage:
            url = self.dnac.url + self.resource
            devices, status = self.crud.get(url,
                                            headers=self.dnac.hdrs,
                                            verify=self.verify,
                                            timeout=self.timeout)
        """
        return self.__crud

# end crud getter

    @property
    def results(self):
        """
        The results method is decorated as if it was an attribute of this
        class and can be used accordingly.  It returns the raw results
        stored in the class' Crud object obtained from an API call.

        Parameters:
            none

        Return Values:
            dict: The results of the API call.

        Usage:
            d = Dnac()
            # CommandRunner is a DnacApi
            cmd = CommandRunner('running-config')
            cmd.formatCmd('<uuid>', 'show run')
            cmd.runSync()
            print str(cmd.results)
        """
        return self.__crud.results

# end results

    @property
    def dnac(self):
        """
        Get method dnac returns the reference to the Dnac instance that
        stores this object.

        Parameters:
            none

        Return Values:
            Dnac object: The Dnac object container.

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(dnac, name, resource)
            dnac = dapi.dnac
        """
        return self.__dnac

# end dnac getter

    @property
    def name(self):
        """
        Get method name returns __name, a user friendly name for accessing
        this object in Dnac's API store, namely Dnac.api{}

        Parameters:
            none

        Return Values:
            str: The DnacApi object's name

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(dnac, name, resource)
            dapi.name
        """
        return self.__name

# end name getter

    @property
    def resource(self):
        """
        Get method resource returns __resource, which is the API call to
        Cisco DNAC.  In child classes, use this method to form requests by
        appending it to Cisco DNAC's base url, i.e. Dnac.url.

        Parameters:
            none

        Return Values:
            str: The API call.

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            d = Dnac()
            dapi = DnacApi(d, name, resource)
            api_call = d.url + dapi.resource
        """
        return self.__resource

# end resource getter

    @property
    def verify(self):
        """
        Get method verify returns value of __verify, which is used to
        determine whether or not to check Cisco DNAC's certificate upon
        making an API call.

        Parameters:
            none

        Return Values:
            boolean: True to check the cert; otherwise, False

        Usage:
            # Do not create a DnacApi object; inherit from it instead
            dapi = DnacApi(d, name, resource)
            dapi.verify
        """
        return self.__verify

# end verify getter

    @property
    def timeout(self):
        """
        Get method timeout returns the value of attribute __timeout.  The
        value returned represents the number of seconds to wait for the
        HTTP server to respond to an API request

        Parameters:
            none

        Return Values:
            int: time to wait in seconds for a response

        Usage:
            dapi = DnacApi(dnac, name, resource)
            dapi.timeout
        """
        return self.__timeout

# end timeout getter

# end class DnacApi()

# begin unit test


if __name__ == '__main__':

    from dnac.dnac import Dnac

    d = Dnac()
    dapi = DnacApi(d, 'aName', '/a/resource/path')

    print('DnacApi:')
    print()
    print('  dnac            = ' + str(type(dapi.dnac)))
    print('  name            = ' + dapi.name)
    print('  crud            = ' + str(type(dapi.crud)))
    print('  results         = ' + str(dapi.results))
    print('  resource        = ' + dapi.resource)
    print('  verify          = ' + str(dapi.verify))
    print('  timeout         = ' + str(dapi.timeout))
    print('  is in api       = ' + str(dapi.name in dapi.dnac.api))
    print('  dapi            = ' + str(dapi))
    print('  dapi in api     = ' + str(d.api[dapi.name]))
    print()
    print('Changing the attributes...')
    print()
    print('Making a get() call...')

    url = d.url + dapi.resource
    results, status = dapi.crud.get(url,
                                    headers=dapi.dnac.hdrs,
                                    verify=dapi.verify,
                                    timeout=dapi.timeout)

    print('  status  = ' + status)
    print('  results = ' + str(results))
    print()
    print('DnacApi: unit test complete.')
