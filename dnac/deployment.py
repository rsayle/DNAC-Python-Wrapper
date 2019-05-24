
from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import ACCEPTED, \
                      REQUEST_NOT_ACCEPTED, \
                      ERROR_MSGS

MODULE = 'deployment.py'

DEPLOYMENT_RESOURCE_PATH = {
                            '1.2.8': '/api/v1/template-programmer/template/deploy/status',
                            '1.2.10': '/api/v1/template-programmer/template/deploy/status'
                           }


class Deployment(DnacApi):
    """
    The Deployment class monitors Cisco DNA Center's progress when pushing
    a template to a set of devices.  When using a Template object to
    apply changes, the Template automatically creates and stores a
    corresponding Deployment instance.  Use the Template to reference the
    Deployment for the job's results.

    Attributes:
        dnac:
            Dnac object: A reference to the Dnac instance that contains
                         the Deployment object
            default: none
            scope: protected
        name:
            str: A user friendly name for the Deployment object and is
                 used as a key for finding it in a Dnac.api attribute.
            default: none
            scope: protected
        id: The UUID pointing to the deploy job's results.
            type: str
            default: none
            scope: protected
        url: The resource path to the deployment job in Cisco DNAC.
            type: str
            default: none
            scope: protected
        status: The deployment job's last known status.
            type: str
            default: none
            scope: protected
        results: The results returned by the deploy operation.
            type: dict
            default: none
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

    Usage:
        d = Dnac()
        template = Template(d, 'Set VLAN')
        d.api['Set VLAN'].deploy()
        print d.api['Set VLAN'].deployment.check_deployment()
    """

    def __init__(self,
                 dnac,
                 id,
                 verify=False,
                 timeout=5):
        """
        Deployment's __init__ method sets up a new Deployment object.
        It takes a Dnac object and the deployment UUID and then constructs
        a Deployment object whose name is 'deployment_<UUID>'.

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: none
                required: yes
            id: The UUID in Cisco DNA Center for the deployment job.
                type: str
                default: none
                required: no
            verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: no
            timeout: The number of seconds to wait for Cisco DNAC's
                     response.
                type: int
                default: 5
                required: no

        Return Values:
            Deployment object: a new Deployment object.

        Usage:
            None.  Template objects automatically create Deployment objects.
        """
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = DEPLOYMENT_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError(
                '__init__: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                           )
        self.__id = id
        self.__url = '%s/%s' % (path, self.__id)
        self.__status = ''  # for monitoring deployment status
        self.__results = {}  # stores deployment's results
        super(Deployment, self).__init__(dnac,
                                         ('deployment_%s' % self.__id),
                                         resource=path,
                                         verify=verify,
                                         timeout=timeout)

# end __init__()

    @property
    def id(self):
        """
        Get method id returns the current value of the object's __id.

        Parameters:
            none

        Return values:
            str: The Deployment's UUID.

        Usage:
            d = Dnac()
            job = Deployment(d, id=<uuid>)
            print job.id
        """
        return self.__id

# end id getter

    @property
    def url(self):
        """
        Get method url returns the current value of the object's __url.

        Parameters:
            none

        Return values:
            str: A resource path to the deployment job.

        Usage:
            d = Dnac()
            job = Deployment(d, id=<uuid>)
            print job.url
        """
        return self.__url

# end url getter

    @property
    def status(self):
        """
        Get method status returns the job's progress stored in __status.

        Parameters:
            none

        Return values:
            str: The job's current deploy progress.

        Usage:
            d = Dnac()
            job = Deployment(d, id=<uuid>)
            print job.status
        """
        return self.__status

# end status getter

    @property
    def results(self):
        """
        Get method results returns the job's response stored in __results.

        Parameters:
            none

        Return values:
            dict: The job's deployment results.

        Usage:
            d = Dnac()
            job = Deployment(d, id=<uuid>)
            print job.results
        """

        return self.__results

# end results getter

    def check_deployment(self):
        """
        Deployment's check_deployment method makes an API call to Cisco
        DNA Center and collects the deploy job's current status and
        and results it returns.  It stores the data received in the
        object's __results and the job's status in __status.  It returns
        __status to the calling function.

        Parameters:
            none

        Return Values:
            str: The job's run status.

        Usage:
            d = Dnac()
            job = Deployment(d, id=<uuid>)
            print job.check_deployment()
        """
        # prepare the API call
        url = self.dnac.url + self.url
        # make the call
        results, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        # return the results
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, 'check_deployment', REQUEST_NOT_ACCEPTED, url,
                ACCEPTED, status, ERROR_MSGS[status], str(results)
                              )
        self.__results = results
        self.__status = self.__results['status']
        return self.__status

# end check_deployment()

# end class Deployment()

# begin unit test


if __name__ == '__main__':

    from dnac.dnac import Dnac
    import pprint

    dnac = Dnac()

    pp = pprint.PrettyPrinter()

    d = Deployment(dnac, 'edaf8986-5670-454a-8252-6fd77b7e1dd9')

    print('Deployment:')
    print()
    print('  type(d)  = ' + str(type(d)))
    print('  name     = ' + d.name)
    print('  id       = ' + d.id)
    print('  resource = ' + d.resource)
    print('  url      = ' + d.url)
    print('  status   = ' + d.status)
    print('  results  = ' + str(d.results))
    print('  self     = ' + str(d))
    print('  in api   = ' + str(d.dnac.api[d.name]))
    print()

    print('Checking the deployment results...')

    d.check_deployment()

    print()
    print('  status  = ' + d.status)
    print('  results = ')
    pp.pprint(d.results)
    print()
    print('Deployment: unit test complete.')
    print()
