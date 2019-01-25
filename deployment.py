#!/usr/bin/env python

from dnac import SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnacapi import DnacApi, \
                    DnacApiError, \
                    REQUEST_NOT_ACCEPTED
import requests
import json

## exceptions

## error messages

INVALID_RESPONSE="Invalid response to API call"

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
                 requestFilter="",
                 verify=False,
                 timeout=5):

        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            self.__respath = \
                "/api/v1/template-programmer/template/deploy/status"
        else:
            raise DeploymentError(
							UNSUPPORTED_DNAC_VERSION + ": %s" % dnac.version
							                   )

        self.__id = id
        self.__url = ""
        self.__status = ""
        self.__results = {}

        super(Deployment, self).__init__(dnac,
                                         name,
                                         resourcePath=self.__respath,
                                         requestFilter=requestFilter,
                                         verify=verify,
                                         timeout=timeout)
        if bool(self.__id): # ID is not empty
            self.name = "deployment_" + self.__id
            self.url = self.respath + "/" + self.__id

## end __init__()

    @property
    def id(self):
        return self.__id

## end id getter

    @id.setter
    def id(self, id):
        self.__id = id
        self.name = "deployment_" + self.__id
        self.__url = self.respath + "/" + self.__id

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
        url = self.dnac.url + self.url + self.filter
        hdrs = self.dnac.hdrs
        # make the call
        resp = requests.request("GET", \
                                url, \
                                headers=hdrs, \
                                verify=self.verify, \
                                timeout=self.timeout)
        # return the results
        if resp.status_code != requests.codes.accepted:
            raise DeploymentError(
                "checkDeployment: %s: %s: %s: expected %s" % \
                (REQUEST_NOT_ACCEPTED, url, str(resp.status_code),
                str(requests.codes.accepted))
                                 )
        self.__results = json.loads(resp.text)
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
    print "  respath = " + d.respath
    print "  url     = " + d.url
    print "  status  = " + d.status
    print "  results = " + str(d.results)
    print
    print "Creating a deployment with an ID..."

    d = Deployment(dnac, "newName", \
                   id="edaf8986-5670-454a-8252-6fd77b7e1dd9")

    print
    print "  type(d) = " + str(type(d))
    print "  name    = " + d.name
    print "  id      = " + d.id
    print "  respath = " + d.respath
    print "  url     = " + d.url
    print "  status  = " + d.status
    print "  results = " + str(d.results)
    print
    print "Resetting deployment to a blank and updating id..."

    d = Deployment(dnac, "aName")
    d.id = "edaf8986-5670-454a-8252-6fd77b7e1dd9"

    print
    print "  type(d) = " + str(type(d))
    print "  name    = " + d.name
    print "  id      = " + d.id
    print "  respath = " + d.respath
    print "  url     = " + d.url
    print "  status  = " + d.status
    print "  results = " + str(d.results)
    print
    print "Resetting deployment to a blank and updating url..."

    d = Deployment(dnac, "aName")
    d.url = d.respath + "/edaf8986-5670-454a-8252-6fd77b7e1dd9"

    print
    print "  type(d) = " + str(type(d))
    print "  name    = " + d.name
    print "  id      = " + d.id
    print "  respath = " + d.respath
    print "  url     = " + d.url
    print "  status  = " + d.status
    print "  results = " + str(d.results)
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

    errors = [INVALID_RESPONSE]

    for e in errors:
        try:
            raiseDeploymentError(e)
        except DeploymentError, e:
            print str(type(e)) + " = " + str(e)

    print
    print "Deployment: unit test complete."
