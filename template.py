#!/user/bin/env python

from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnacapi import DnacApi, \
                    DnacApiError
from crud import OK, \
                 REQUEST_NOT_OK, \
                 ACCEPTED, \
                 REQUEST_NOT_ACCEPTED, \
                 ERROR_MSGS
from deployment import Deployment
import json

## globals

MODULE="template.py"

# values instructing Cisco DNA Center how to interpret the target ID value
TARGET_BY_DEFAULT="DEFAULT"
TARGET_BY_ID="MANAGED_DEVICE_UUID"
TARGET_BY_HOSTNAME="MANAGED_DEVICE_HOSTNAME"
TARGET_BY_IP="MANAGED_DEVICE_IP"
TARGET_BY_SERIAL="PRE_PROVISIONED_SERIAL"
TARGET_BY_MAC="PRE_PROVISIONED_SERIAL"

VALID_TARGET_TYPES=[TARGET_BY_DEFAULT, \
                    TARGET_BY_ID, \
                    TARGET_BY_HOSTNAME, \
                    TARGET_BY_IP, \
                    TARGET_BY_SERIAL, \
                    TARGET_BY_MAC]

# deployment states returned when checking on a deployment's status
DEPLOYMENT_INIT="INIT"
DEPLOYMENT_SUCCESS="SUCCESS"
DEPLOYMENT_FAILURE="FAILURE"

VALID_DEPLOYMENT_STATES=[DEPLOYMENT_INIT, \
                         DEPLOYMENT_SUCCESS, \
                         DEPLOYMENT_FAILURE]

## end globals

## exceptions

## error messages
TEMPLATE_NOT_FOUND="Could not find template"
NO_TEMPLATES_FOUND="Could not retrieve any templates"
INVALID_RESPONSE="Invalid response to API call"
EMPTY_TEMPLATE="Template has no data or does not exist"
ILLEGAL_TARGET_TYPE="Illegal target type"
UNKNOWN_DEPLOYMENT_STATUS="Unknown deployment status"
ALREADY_DEPLOYED="Template already deployed"
ILLEGAL_VERSION="Illegal template version"
UNKNOWN_VERSION="Unknown template version"

class TemplateError(DnacApiError):

    def __init__(self, msg):
        super(TemplateError, self).__init__(msg)

## end class TemplateError()

## end exceptions

class Template(DnacApi):

    def __init__(self,
                 dnac,
                 name,
                 version=0,
                 verify=False,
                 timeout=5):
        # version is the template's version and must not be negative
        if version < 0:
            raise TemplateError(
                "__init__: %s: must not be negative: %s" %
                (ILLEGAL_VERSION, str(version))
                               )
        # check Cisco DNA Center's version and set the resource path
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = "/dna/intent/api/v1/template-programmer/template"
        else:
            raise DnacError(
                "__init__: %s: %s" %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                               )
        # setup initial attribute values
        self.__templateId = "" # base template ID
        self.__version = version # requested template version, 0 = latest
        self.__versionedTemplate = {} 
        self.__versionedTemplateId = "" # template that can be deployed
        self.__versionedTemplateParams = {}
        self.__targetId = "" # where to deploy the template
        self.__targetType = TARGET_BY_DEFAULT # how to find the target
        self.__deployment = "" # object for monitoring the deployment
        super(Template, self).__init__(dnac,
                                       name,
                                       resource=path,
                                       verify=verify,
                                       timeout=timeout)
        # retrieve the template ID by its name
        self.__templateId = self.getTemplateIdByName(self.name)
        if not self.__templateId: # template could not be found
            raise TemplateError(
                "__init__: %s: %s" % (TEMPLATE_NOT_FOUND, self.name)
                               )
        # retrieve the versioned template
        self.__versionedTemplate = \
            self.getVersionedTemplateByName(self.name, self.__version)
        if not bool(self.__versionedTemplate): # template is empty
            raise TemplateError(
                "__init__: %s: %s version %s" % 
                (UNKNOWN_VERSION, self.name, str(self.__version))
                               )

## end __init__()

    @property
    def templateId(self):
        return self.__templateId

## end templateId getter

    @templateId.setter
    def templateId(self, templateId):
        self.__templateId = templateId

## end templateId setter

    @property
    def version(self):
        return self.__version

## end version getter

    @version.setter
    def version(self, version):
        self.__version = version

## end version setter

    @property
    def versionedTemplate(self):
        return self.__versionedTemplate

## end versionedTemplate getter

    @versionedTemplate.setter
    def versionedTemplate(self, versionedTemplate):
        self.__versionedTemplate = versionedTemplate

## end versionedTemplate setter

    @property
    def versionedTemplateId(self):
        return self.__versionedTemplateId

## end versionedTemplateId getter

    @versionedTemplateId.setter
    def versionedTemplateId(self, versionedTemplateId):
        self.__versionedTemplateId = versionedTemplateId

## end versionedTemplateId setter

    @property
    def versionedTemplateParams(self):
        return self.__versionedTemplateParams

## end versionedTemplateParams getter

    @versionedTemplateParams.setter
    def versionedTemplateParams(self, versionedTemplateParams):
        self.__versionedTemplateParams = versionedTemplateParams

## end versionedTemplateParams setter

    @property
    def targetId(self):
        return self.__targetId

## end targetId getter

    @targetId.setter
    def targetId(self, targetId):
        self.__targetId = targetId

## end targetId setter

    @property
    def targetType(self):
        return self.__targetType

## end targetType getter

    @targetType.setter
    def targetType(self, targetType):
        self.__targetType = targetType

## end targetType setter

    @property
    def deployment(self):
        return self.__deployment

## end deployment getter

    @deployment.setter
    def deployment(self, deployment):
        self.__deployment = deployment

## end deployment setter

    def getAllTemplates(self):
        url = self.dnac.url + self.resource
        templates, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, "checkDeployment", REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(results)
                              )
        return templates

## end getAllTemplates()

    def getTemplateById(self, id):
        url = self.dnac.url + self.resource + "/" + id
        template, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, "getTemplateById", REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(results)
                              )
        return template

## end getTemplateById

    def getTemplateIdByName(self, name):
        self.__templateId = ""
        # find the template by name
        templates = self.getAllTemplates()
        if bool(templates): # templates is not empty
            for template in templates:
                # find the template by name, save it and save its ID
                if template['name'] == name:
                    self.__templateId = template['templateId']
                else: # keep looking for the template by its name
                    continue
        else:
            raise TemplateError(
                "getTemplateIdByName: %s:" % NO_TEMPLATES_FOUND
                               )
        # all done - return the template
        return self.__templateId

## end getTemplateByName()

    def getVersionedTemplateByName(self, name, ver):
        # version is the template's version and must not be negative
        if ver < 0:
            raise TemplateError(
              "getVersionedTemplateByName: %s: %s: %s \
              must not be negative: %s" %
              (ILLEGAL_VERSION, name, str(ver))
                               )
        # reset the versioned template information
        self.__versionedTemplate = {}
        self.__versionedTemplateId = ""
        self.__versionedTemplateParams = {}
        # find the versioned template by name
        templates = self.getAllTemplates()
        if bool(templates): # templates is not empty
            for template in templates:
                # find the versioned template by name and save its UUID
                if template['name'] == name:
                    versions = template['versionsInfo']
                    if ver > 0:
                        # get the version requested
                        for version in versions:
                            # DNAC uses a string for the version
                            if ver == int(version['version']):
                                # got it - set the versioned template id
                                # and move on
                                self.__versionedTemplateId = version['id']
                                break
                            else:
                                # haven't found it - continue searching
                                continue
                        if not self.__versionedTemplateId:
                            # version is greater than any versions
                            raise TemplateError(
                                "getVersionedTemplateByName: %s: %s: %s" %
                                (UNKNOWN_VERSION, name, str(ver))
                                               )
                    elif ver == 0:
                        # get the latest version
                        latest = versions[0]
                        for version in versions:
                            if version['version'] <= latest['version']:
                                # not the latest version - keep going
                                continue
                            else:
                                # more recent version - save and continue
                                latest = version
                                continue
                        # got the latest version - save it
                        self.__version = latest['version']
                        self.__versionedTemplateId = latest['id']
                else: # keep looking for the template by its name
                    continue
            # get the versioned template using its id
            self.__versionedTemplate = \
                self.getTemplateById(self.__versionedTemplateId)
            # collect the template's parameters
            if bool(self.__versionedTemplate): # template not empty
                params = self.__versionedTemplate['templateParams']
                if bool(params): # parameter list is not empty
                    for param in params:
                        self.__versionedTemplateParams\
                            [param['parameterName']] = \
                             param['defaultValue']
                # otherwise there are no parameters - keep going
            else:
                raise TemplateError(
                    "getVersionedTemplateByName: %s: %s: %s" %
                    (EMPTY_TEMPLATE, name, self.__versionedTemplateId)
                                   )
        else:
            raise TemplateError(
                "getVersionedTemplateByName: %s: %s" % 
                (NO_TEMPLATES_FOUND, name)
                               )
        return self.__versionedTemplate

## end getVersionedTemplateByName()

    def makeBody(self):
        tgtinfo = {}
        tgtinfo['type'] = self.__targetType
        tgtinfo['id'] = self.__targetId
        tgtinfo['params'] = self.__versionedTemplateParams
        targetInfo = []
        targetInfo.append(tgtinfo)
        body = {}
        body['templateId'] = self.__versionedTemplateId
        body['targetInfo'] = targetInfo
        return json.dumps(body)

## end makeBody()

    def deploy(self):
        url = self.dnac.url + self.resource + "/deploy"
        body = self.makeBody()
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=body,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, "checkDeployment", REQUEST_NOT_ACCEPTED, url,
                ACCEPTED, status, ERROR_MSGS[status], str(results)
                              )
        # make a deployment object
        did = results['deploymentId']
        elts = did.split()
        deployId = elts[len(elts) - 1]
        self.__deployment = Deployment(self.dnac, 
                                       "deployment_", 
                                       id=deployId)
        return self.__deployment.checkDeployment()

## end deploy()

    def deploySync(self, wait=3):
        url = self.dnac.url + self.resource + "/deploy"
        body = self.makeBody()
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=body,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            raise DnacApiError(
                MODULE, "checkDeployment", REQUEST_NOT_ACCEPTED, url,
                ACCEPTED, status, ERROR_MSGS[status], str(results)
                              )
        # make a deployment object
        did = result['deploymentId']
        elts = did.split()
        deployId = elts[len(elts) - 1]
        self.__deployment = Deployment(self.dnac,
                                       "deployment_",
                                       id=deployId)
        self.deployment.checkDeployment()
        while self.deployment.status == DEPLOYMENT_INIT:
            time.sleep(wait)
            self.deployment.checkDeployment()
        return self.deployment.status

## end class Template()

## begin unit test

if __name__ == '__main__':

    from dnac import Dnac
    import time

    d = Dnac()
    t = Template(d, "MGM Set VLAN")

    print "Template:"
    print 
    print " type(t)                 = " + str(type(t))
    print " name                    = " + t.name
    print " resource                = " + t.resource
    print " templateId              = " + t.templateId
    print " version                 = " + str(t.version)
    print " versionedTemplate       = " + str(t.versionedTemplate)
    print " versionedTemplateId     = " + t.versionedTemplateId
    print " versionedTemplateParams = " + str(t.versionedTemplateParams)
    print " targetId                = " + t.targetId
    print " targetType              = " + t.targetType
    print " deployment              = " + t.deployment
    print
    print "Trying an earlier version of the template..."

    t = Template(d, "MGM Set VLAN", version=1)

    print 
    print " type(t)                 = " + str(type(t))
    print " name                    = " + t.name
    print " resource                = " + t.resource
    print " templateId              = " + t.templateId
    print " version                 = " + str(t.version)
    print " versionedTemplate       = " + str(t.versionedTemplate)
    print " versionedTemplateId     = " + t.versionedTemplateId
    print " versionedTemplateParams = " + str(t.versionedTemplateParams)
    print " targetId                = " + t.targetId
    print " targetType              = " + t.targetType
    print " deployment              = " + t.deployment
    print

    print "Resetting the template to the latest..."
    print

    t = Template(d, "MGM Set VLAN")

    print "Setting the versioned template's parameters..."
    print
    print " version                 = " + str(t.version)
    print " versionedTemplate       = " + str(t.versionedTemplate)
    print " versionedTemplateId     = " + t.versionedTemplateId
    print " versionedTemplateParams = " + str(t.versionedTemplateParams)
    print

    t.versionedTemplateParams['interface'] = "gig1/0/1"
    t.versionedTemplateParams['description'] = "Configured by template.py"
    t.versionedTemplateParams['vlan'] = 60

    print " interface   = " + t.versionedTemplateParams['interface']
    print " description = " + t.versionedTemplateParams['description']
    print " vlan        = " + str(t.versionedTemplateParams['vlan'])
    print
    print "Build the request body..."
    print

    t.targetId = "a0116157-3a02-4b8d-ad89-45f45ecad5da"
    t.targetType = TARGET_BY_ID
    body = t.makeBody()

    print " body = " + body
    print
    print "Deploying the template asynchronously..."
    print

    status = t.deploy()

    print " status           = " + str(status)
    print " type(deployment) = " + str(t.deployment)
    print " deployment.name  = " + t.deployment.name
    print " deployment.id    = " + t.deployment.id
    print
    print "Checking deployment..."
    
    while status == DEPLOYMENT_INIT:
        print " status = " + status
        time.sleep(1)
        status = t.deployment.checkDeployment()

    print " status          = " + status
    print " results[status] = " + t.deployment.results['status']
    print " results         = " + str(t.deployment.results)
    print
    print "Template: unit test complete."

