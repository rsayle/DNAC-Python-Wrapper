#!/usr/bin/env python

from dnac import SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnacapi import DnacApi, \
                    DnacApiError
from crud import ACCEPTED, \
                 REQUEST_NOT_ACCEPTED

## exceptions


class DeploymentError(DnacApiError):

    def __init__(self, msg):
        super(DeploymentError, self).__init__(msg)

## end class DeploymentError

## end exceptions

class Deployment(DnacApi):

    def __init__(self,
                 dnac,
                 name,
                 id="",
                 verify=False,
                 timeout=5):

        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = "/api/v1/template-programmer/template/deploy/status"
        else:
            raise DeploymentError(
		UNSUPPORTED_DNAC_VERSION + ": %s" % dnac.version
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
        if bool(self.__id): # ID is not empty
            self.name = "deployment_" + self.__id
            self.url = self.resource + "/" + self.__id

## end __init__()

    @property
    def id(self):
        return self.__id

## end id getter

    @id.setter
    def id(self, id):
        self.__id = id
        self.name = "deployment_" + self.__id
        self.__url = self.resource + "/" + self.__id

## end id setter

    @property
    def url(self):
        return self.__url

## end url getter

    @url.setter
    def url(self, url):
        self.__url = url
        pathElts = url.split("/")
        self.__id = pathElts[ len(pathElts) - 1 ]
        self.name = "deployment_" + self.__id

## end url setter

    @property
    def status(self):
        return self.__status

## end status getter

    @status.setter
    def status(self, status):
        self.__status = status

## end status setter

    @property
    def results(self):
        return self.__results

## end results getter

    @results.setter
    def results(self, results):
        self.__results = results

## end results setter

    def checkDeployment(self):
        # prepare the API call
        url = self.dnac.url + self.url
        # make the call
        results, status = self.crud.get(url,
                                     headers=self.dnac.hdrs,
                                     verify=self.verify,
                                     timeout=self.timeout)
        # return the results
        if status != ACCEPTED:
            raise DeploymentError(
                "checkDeployment: %s: %s: %s: expected %s" % \
                (REQUEST_NOT_ACCEPTED, url, status, ACCEPTED)
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
    print
    print "Resetting deployment to a blank and updating id..."

    d = Deployment(dnac, "aName")
    d.id = "edaf8986-5670-454a-8252-6fd77b7e1dd9"

    print
    print "  type(d)  = " + str(type(d))
    print "  name     = " + d.name
    print "  id       = " + d.id
    print "  resource = " + d.resource
    print "  url      = " + d.url
    print "  status   = " + d.status
    print "  results  = " + str(d.results)
    print
    print "Resetting deployment to a blank and updating url..."

    d = Deployment(dnac, "aName")
    d.url = d.resource + "/edaf8986-5670-454a-8252-6fd77b7e1dd9"

    print
    print "  type(d)  = " + str(type(d))
    print "  name     = " + d.name
    print "  id       = " + d.id
    print "  resource = " + d.resource
    print "  url      = " + d.url
    print "  status   = " + d.status
    print "  results  = " + str(d.results)
    print
    print "Checking the deployment results..."

    d.checkDeployment()

    print
    print "  status  = " + d.status
    print "  results = " + str(d.results)
    print
    print "Testing exceptions..."

    def raiseDeploymentError(msg):
        raise DeploymentError(msg)

    errors = [REQUEST_NOT_ACCEPTED]

    for e in errors:
        try:
            raiseDeploymentError(e)
        except DeploymentError, e:
            print str(type(e)) + " = " + str(e)

    print
    print "Deployment: unit test complete."
