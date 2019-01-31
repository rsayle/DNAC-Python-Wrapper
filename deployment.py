#!/usr/bin/env python

from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnacapi import DnacApi, \
                    DnacApiError
from crud import ACCEPTED, \
                 REQUEST_NOT_ACCEPTED, \
                 ERROR_MSGS

MODULE="deployment.py"

class Deployment(DnacApi):
    '''
    The Deployment class monitors Cisco DNA Center's progress when pushing
    a template to a set of devices.  When using a Template object to
    apply changes, the Template automatically creates and stores a
    corresponding Deployment instance.  Use the Template to reference the
    Deployment for the job's results.

    Attributes:
        dnac:
            Dnac object: A reference to the Dnac instance that contains
                         the Deployment object
            default: None
        name:
            str: A user friendly name for the Deployment object and is
                 used as a key for finding it in a Dnac.api attribute.
            default: None
        id: The UUID pointing to the deploy job's results.
            type: str
            default: None
        url: The resource path to the deployment job in Cisco DNAC.
            type: str
            default: None
        status: The deployment job's last known status.
            type: str
            default: None
        results: The results returned by the deploy operation.
            type: dict
            default: None
        verify: Flag indicating whether or not the request should verify
                Cisco DNAC's certificate.
            type: boolean
            default: False
        timeout: The number of seconds the request for a token should wait
                 before assuming Cisco DNAC is unavailable.
            type: int
            default: 5

    Usage:
        d = Dnac()
        template = Template(d, 'Set VLAN')
        d.api['Set VLAN'].deploy()
        print d.api['Set VLAN'].deployment.checkDeployment()
    '''
    def __init__(self,
                 dnac,
                 name,
                 id="",
                 verify=False,
                 timeout=5):
        '''
        Deployment's __init__ method sets up a new Deployment object.  The
        method overrides whatever name is given if a UUID for the deploy
        job is also provided as id keyword argument.  In that case, the
        Deployment object's name is changed to "deployment_<UUID>".

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: None
                required: Yes
            name: A user friendly name for find this object in a Dnac
                  instance.
                type: str
                default: None
                required: Yes
            id: The UUID in Cisco DNA Center for the deployment job.
                type: str
                default: None
                required: no
            verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: No
            timeout: The number of seconds to wait for Cisco DNAC's
                     response.
                type: int
                default: 5
                required: No

        Return Values:
            Deployment object: a new Deployment object.

        Usage:
            d = Dnac()
            job = Deployment(d, "aJob")
            # Template objects automatically create Deployment objects.
            # Creating your own should be rarely necessary.
        '''
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = "/api/v1/template-programmer/template/deploy/status"
        else:
            raise DnacError(
                "__init__: %s: %s" %
		(UNSUPPORTED_DNAC_VERSION, dnac.version)
	                    )
        self.__id = id
        self.__url = "" # auto set by name and id
        self.__status = "" # for monitoring deployment status
        self.__results = {} # stores deployment's results
        super(Deployment, self).__init__(dnac,
                                         name,
                                         resource=path,
                                         verify=verify,
                                         timeout=timeout)
        if bool(self.__id): # a UUID was given to the constructor
            self.name = "deployment_" + self.__id
            self.__url = self.resource + "/" + self.__id

## end __init__()

    @property
    def id(self):
        '''
        Get method id returns the current value of the object's __id.

        Parameters:
            None

        Return values:
            str: The Deployment's UUID.

        Usage:
            d = Dnac()
            job = Deployment(d, "aJob", id=<uuid>)
            print job.id
        '''
        return self.__id

## end id getter

    @id.setter
    def id(self, id):
        '''
        Set method id changes __id to be the UUID passed.  It also updates
        the object's name and url fields for consistency:
            id = "<uuid>"
            name = "deployment_<uuid>"
            url = "self.resource/<uuid>"

        Parameters:
            id: The new UUID for the deploy job.
                type: str
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            d = Dnac()
            job = Deployment(d, "aJob")
            job.id = "<uuid>"
        '''
        self.__id = id
        self.name = "deployment_" + self.__id
        self.__url = self.resource + "/" + self.__id

## end id setter

    @property
    def url(self):
        '''
        Get method url returns the current value of the object's __url.

        Parameters:
            None

        Return values:
            str: A resource path to the deployment job.

        Usage:
            d = Dnac()
            job = Deployment(d, "aJob", id=<uuid>)
            print job.url
        '''
        return self.__url

## end url getter

    @url.setter
    def url(self, url):
        '''
        Set method url changes __url to be the resource path given as its
        parameter.  It assumes the last value in the resource path is the
        UUID for the deployment job, and it updates the name and id field
        swith this value.
            url = "self.resource/<uuid>"
            name = "deployment_<uuid>"
            id = "<uuid>"

        Parameters:
            id: The new UUID for the deploy job.
                type: str
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            d = Dnac()
            job = Deployment(d, "aJob")
            job.id = "<uuid>"
        '''
        self.__url = url
        pathElts = url.split("/")
        self.__id = pathElts[ len(pathElts) - 1 ]
        self.name = "deployment_" + self.__id

## end url setter

    @property
    def status(self):
        '''
        Get method status returns the job's progress stored in __status.

        Parameters:
            None

        Return values:
            str: The job's current deploy progress.

        Usage:
            d = Dnac()
            job = Deployment(d, "aJob", id=<uuid>)
            print job.status
        '''
        return self.__status

## end status getter

    @status.setter
    def status(self, status):
        '''
        The status set method updates the __status attribute.

        Parameters:
            status:
                type: str
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            d = Dnac()
            job = Deployment(d, "aJob", id=<uuid>)
            progress = job.status
        '''
        self.__status = status

## end status setter

    @property
    def results(self):
        '''
        Get method results returns the job's response stored in __results.

        Parameters:
            None

        Return values:
            dict: The job's deployment results.

        Usage:
            d = Dnac()
            job = Deployment(d, "aJob", id=<uuid>)
            print job.results
        '''
        return self.__results

## end results getter

    @results.setter
    def results(self, results):
        '''
        The results set method updates the __results attribute.

        Parameters:
            results:
                type: dict
                default: None
                required: Yes

        Return Values:
            None

        Usage:
            d = Dnac()
            job = Deployment(d, "aJob", id=<uuid>)
            job.results, status = job.crud.get(job.url, job.dnac.hdrs)
        '''
        self.__results = results

## end results setter

    def checkDeployment(self):
        '''
        Deployment's checkDeployment method makes an API call to Cisco
        DNA Center and collects the deploy job's current status and
        and results it returns.  It stores the data received in the
        object's __results and the job's status in __status.  It returns
        __status to the calling function.

        Parameters:
            None

        Return Values:
            str: The job's run status.

        Usage:
            d = Dnac()
            job = Deployment(d, "aJob", id=<uuid>)
            print job.checkDeployment
        '''
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
                MODULE, "checkDeployment", REQUEST_NOT_ACCEPTED, url,
                ACCEPTED, status, ERROR_MSGS[status], str(results)
                              )
        self.__results = results
        self.__status = self.__results['status']
        return self.__status

## end class Deployment()

## begin unit test

if __name__ == '__main__':

    from dnac import Dnac

    dnac = Dnac()

    d = Deployment(dnac, "aName")

    print "Deployment:"
    print
    print "  type(d) = " + str(type(d))
    print "  name    = " + d.name
    print "  id      = " + d.id
    print "  resource = " + d.resource
    print "  url     = " + d.url
    print "  status  = " + d.status
    print "  results = " + str(d.results)
    print "  self    = " + str(d)
    print "  in api  = " + str(d.dnac.api[d.name])
    print
    print "Creating a deployment with an ID..."

    d = Deployment(dnac, "newName", \
                   id="edaf8986-5670-454a-8252-6fd77b7e1dd9")

    print
    print "  type(d)  = " + str(type(d))
    print "  name     = " + d.name
    print "  id       = " + d.id
    print "  resource = " + d.resource
    print "  url      = " + d.url
    print "  status   = " + d.status
    print "  results  = " + str(d.results)
    print "  self     = " + str(d)
    print "  keys     = " + str(d.dnac.api.keys())
    print "  in api   = " + str(d.dnac.api[d.name])
    print
    print "Updating the ID..."

    d.id = "a-fake-id"

    print
    print "  type(d)  = " + str(type(d))
    print "  name     = " + d.name
    print "  id       = " + d.id
    print "  resource = " + d.resource
    print "  url      = " + d.url
    print "  status   = " + d.status
    print "  results  = " + str(d.results)
    print "  self    = " + str(d)
    print "  in api  = " + str(d.dnac.api[d.name])
    print
    print "Updating the URL..."

    d.url = d.resource + "/edaf8986-5670-454a-8252-6fd77b7e1dd9"

    print
    print "  type(d)  = " + str(type(d))
    print "  name     = " + d.name
    print "  id       = " + d.id
    print "  resource = " + d.resource
    print "  url      = " + d.url
    print "  status   = " + d.status
    print "  results  = " + str(d.results)
    print "  self    = " + str(d)
    print "  in api  = " + str(d.dnac.api[d.name])
    print
    print "Checking the deployment results..."

    d.checkDeployment()

    print
    print "  status  = " + d.status
    print "  results = " + str(d.results)
    print
    print "Deployment: unit test complete."
